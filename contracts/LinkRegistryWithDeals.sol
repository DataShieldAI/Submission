// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import "./DealClient.sol";

contract LinkRegistryWithDeals {
    enum Status { CLEAN, DMCA_REQUESTED }

    struct LinkRecord {
        string url;
        string licenseCID;
        string dmcaCID;
        Status status;
        uint256 timestamp;
        bool exists;

        bytes32 dealProposalLicense;
        bytes32 dealProposalDMCA;
    }

    mapping(string => LinkRecord) public linkRecords;
    string[] public allLinks;

    address public owner;
    DealClient public dealClient;

    event LinkAdded(string url, string licenseCID, bytes32 licenseDealId);
    event DMCAFiled(string url, string dmcaCID, bytes32 dmcaDealId);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    constructor(address dealClientAddr) {
        owner = msg.sender;
        dealClient = DealClient(dealClientAddr);
    }

    function addLinkWithDeal(
        string calldata url,
        string calldata licenseCID,
        uint64 size
    ) external onlyOwner {
        require(!linkRecords[url].exists, "Link already exists");

        bytes memory cidBytes = bytes(licenseCID);

        DealClient.DealRequest memory req = DealClient.DealRequest({
            piece_cid: cidBytes,
            piece_size: size,
            verified_deal: false,
            label: url,
            start_epoch: int64(uint64(block.timestamp) + 100), // dummy epoch logic
            end_epoch: int64(uint64(block.timestamp) + 1000000),
            storage_price_per_epoch: 0,
            provider_collateral: 0,
            client_collateral: 0
        });

        bytes32 licenseDealId = dealClient.makeDealProposal(req);

        linkRecords[url] = LinkRecord({
            url: url,
            licenseCID: licenseCID,
            dmcaCID: "",
            status: Status.CLEAN,
            timestamp: block.timestamp,
            exists: true,
            dealProposalLicense: licenseDealId,
            dealProposalDMCA: 0
        });

        allLinks.push(url);
        emit LinkAdded(url, licenseCID, licenseDealId);
    }

    function fileDMCAWithDeal(
        string calldata url,
        string calldata dmcaCID,
        uint64 size
    ) external onlyOwner {
        require(linkRecords[url].exists, "Link does not exist");

        bytes memory cidBytes = bytes(dmcaCID);

        DealClient.DealRequest memory req = DealClient.DealRequest({
            piece_cid: cidBytes,
            piece_size: size,
            verified_deal: false,
            label: url,
            start_epoch: int64(uint64(block.timestamp) + 100),
            end_epoch: int64(uint64(block.timestamp) + 1000000),
            storage_price_per_epoch: 0,
            provider_collateral: 0,
            client_collateral: 0
        });

        bytes32 dmcaDealId = dealClient.makeDealProposal(req);

        linkRecords[url].dmcaCID = dmcaCID;
        linkRecords[url].status = Status.DMCA_REQUESTED;
        linkRecords[url].dealProposalDMCA = dmcaDealId;

        emit DMCAFiled(url, dmcaCID, dmcaDealId);
    }

    function getLinkCount() external view returns (uint256) {
        return allLinks.length;
    }
}
