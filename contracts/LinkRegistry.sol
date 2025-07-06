// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

/// @title LinkRegistry
/// @notice Register links and their license/DMCA IPFS hashes
contract LinkRegistry {
    enum Status {
        CLEAN,
        DMCA_REQUESTED
    }

    struct LinkRecord {
        string url;         // URL of the repo/resource
        string licenseCID;  // IPFS CID of license doc
        string dmcaCID;     // IPFS CID of DMCA PDF
        Status status;
        uint256 timestamp;
        bool exists;
    }

    mapping(string => LinkRecord) public linkRecords;
    string[] public allLinks;

    address public owner;

    event LinkAdded(string url, string licenseCID, uint256 timestamp);
    event DMCAFiled(string url, string dmcaCID, uint256 timestamp);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function addLink(string calldata url, string calldata licenseCID) external onlyOwner {
        require(!linkRecords[url].exists, "Link already exists");
        linkRecords[url] = LinkRecord({
            url: url,
            licenseCID: licenseCID,
            dmcaCID: "",
            status: Status.CLEAN,
            timestamp: block.timestamp,
            exists: true
        });
        allLinks.push(url);
        emit LinkAdded(url, licenseCID, block.timestamp);
    }

    function fileDMCA(string calldata url, string calldata dmcaCID) external onlyOwner {
        require(linkRecords[url].exists, "Link does not exist");
        linkRecords[url].dmcaCID = dmcaCID;
        linkRecords[url].status = Status.DMCA_REQUESTED;
        emit DMCAFiled(url, dmcaCID, block.timestamp);
    }

    function getLinkCount() external view returns (uint256) {
        return allLinks.length;
    }
}
