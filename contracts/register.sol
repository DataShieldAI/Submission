// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title GitHubRepoProtection
 * @dev Smart contract for registering and protecting GitHub repositories
 */
contract GitHubRepoProtection is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    
    Counters.Counter private _repoIds;
    Counters.Counter private _violationIds;
    
    struct Repository {
        uint256 id;
        address owner;
        string githubUrl;
        string repoHash;
        string codeFingerprint;
        string[] keyFeatures;
        string licenseType;
        uint256 registeredAt;
        bool isActive;
        string ipfsMetadata;
    }
    
    struct CodeViolation {
        uint256 id;
        uint256 originalRepoId;
        address reporter;
        string violatingUrl;
        string evidenceHash;
        uint256 similarityScore; // 0-100
        ViolationStatus status;
        uint256 reportedAt;
        string dmcaReference;
    }
    
    enum ViolationStatus {
        Pending,
        Verified,
        Disputed,
        Resolved,
        Rejected
    }
    
    // Mappings
    mapping(uint256 => Repository) public repositories;
    mapping(uint256 => CodeViolation) public violations;
    mapping(address => uint256[]) public userRepositories;
    mapping(string => uint256) public repoHashToId;
    mapping(uint256 => uint256[]) public repoViolations;
    
    // Events
    event RepositoryRegistered(
        uint256 indexed repoId,
        address indexed owner,
        string githubUrl,
        string repoHash
    );
    
    event ViolationReported(
        uint256 indexed violationId,
        uint256 indexed originalRepoId,
        address indexed reporter,
        string violatingUrl,
        uint256 similarityScore
    );
    
    event ViolationStatusUpdated(
        uint256 indexed violationId,
        ViolationStatus newStatus,
        string dmcaReference
    );
    
    event LicenseUpdated(
        uint256 indexed repoId,
        string newLicense
    );
    
    // Modifiers
    modifier onlyRepoOwner(uint256 repoId) {
        require(repositories[repoId].owner == msg.sender, "Not repository owner");
        _;
    }
    
    modifier validRepo(uint256 repoId) {
        require(repositories[repoId].id != 0, "Repository does not exist");
        require(repositories[repoId].isActive, "Repository is not active");
        _;
    }
    
    /**
     * @dev Register a new GitHub repository for protection
     */
    function registerRepository(
        string memory githubUrl,
        string memory repoHash,
        string memory codeFingerprint,
        string[] memory keyFeatures,
        string memory licenseType,
        string memory ipfsMetadata
    ) external nonReentrant returns (uint256) {
        require(bytes(githubUrl).length > 0, "GitHub URL required");
        require(bytes(repoHash).length > 0, "Repository hash required");
        require(repoHashToId[repoHash] == 0, "Repository already registered");
        
        _repoIds.increment();
        uint256 newRepoId = _repoIds.current();
        
        repositories[newRepoId] = Repository({
            id: newRepoId,
            owner: msg.sender,
            githubUrl: githubUrl,
            repoHash: repoHash,
            codeFingerprint: codeFingerprint,
            keyFeatures: keyFeatures,
            licenseType: licenseType,
            registeredAt: block.timestamp,
            isActive: true,
            ipfsMetadata: ipfsMetadata
        });
        
        userRepositories[msg.sender].push(newRepoId);
        repoHashToId[repoHash] = newRepoId;
        
        emit RepositoryRegistered(newRepoId, msg.sender, githubUrl, repoHash);
        
        return newRepoId;
    }
    
    /**
     * @dev Report a code violation
     */
    function reportViolation(
        uint256 originalRepoId,
        string memory violatingUrl,
        string memory evidenceHash,
        uint256 similarityScore
    ) external validRepo(originalRepoId) nonReentrant returns (uint256) {
        require(bytes(violatingUrl).length > 0, "Violating URL required");
        require(similarityScore <= 100, "Invalid similarity score");
        require(similarityScore >= 70, "Similarity score too low"); // Minimum threshold
        
        _violationIds.increment();
        uint256 newViolationId = _violationIds.current();
        
        violations[newViolationId] = CodeViolation({
            id: newViolationId,
            originalRepoId: originalRepoId,
            reporter: msg.sender,
            violatingUrl: violatingUrl,
            evidenceHash: evidenceHash,
            similarityScore: similarityScore,
            status: ViolationStatus.Pending,
            reportedAt: block.timestamp,
            dmcaReference: ""
        });
        
        repoViolations[originalRepoId].push(newViolationId);
        
        emit ViolationReported(
            newViolationId,
            originalRepoId,
            msg.sender,
            violatingUrl,
            similarityScore
        );
        
        return newViolationId;
    }
    
    /**
     * @dev Update violation status (owner or authorized agent)
     */
    function updateViolationStatus(
        uint256 violationId,
        ViolationStatus newStatus,
        string memory dmcaReference
    ) external {
        CodeViolation storage violation = violations[violationId];
        require(violation.id != 0, "Violation does not exist");
        
        Repository memory repo = repositories[violation.originalRepoId];
        require(
            msg.sender == repo.owner || msg.sender == owner(),
            "Not authorized"
        );
        
        violation.status = newStatus;
        if (bytes(dmcaReference).length > 0) {
            violation.dmcaReference = dmcaReference;
        }
        
        emit ViolationStatusUpdated(violationId, newStatus, dmcaReference);
    }
    
    /**
     * @dev Update repository license
     */
    function updateLicense(
        uint256 repoId,
        string memory newLicense
    ) external onlyRepoOwner(repoId) {
        repositories[repoId].licenseType = newLicense;
        emit LicenseUpdated(repoId, newLicense);
    }
    
    /**
     * @dev Deactivate repository
     */
    function deactivateRepository(uint256 repoId) external onlyRepoOwner(repoId) {
        repositories[repoId].isActive = false;
    }
    
    /**
     * @dev Get repository details
     */
    function getRepository(uint256 repoId) external view returns (Repository memory) {
        return repositories[repoId];
    }
    
    /**
     * @dev Get violation details
     */
    function getViolation(uint256 violationId) external view returns (CodeViolation memory) {
        return violations[violationId];
    }
    
    /**
     * @dev Get user's repositories
     */
    function getUserRepositories(address user) external view returns (uint256[] memory) {
        return userRepositories[user];
    }
    
    /**
     * @dev Get repository violations
     */
    function getRepositoryViolations(uint256 repoId) external view returns (uint256[] memory) {
        return repoViolations[repoId];
    }
    
    /**
     * @dev Get repository by hash
     */
    function getRepositoryByHash(string memory repoHash) external view returns (Repository memory) {
        uint256 repoId = repoHashToId[repoHash];
        require(repoId != 0, "Repository not found");
        return repositories[repoId];
    }
    
    /**
     * @dev Get total repositories count
     */
    function getTotalRepositories() external view returns (uint256) {
        return _repoIds.current();
    }
    
    /**
     * @dev Get total violations count
     */
    function getTotalViolations() external view returns (uint256) {
        return _violationIds.current();
    }
}