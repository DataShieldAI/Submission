// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import {MarketAPI} from "filecoin-solidity-api/contracts/v0.8/MarketAPI.sol";
import {MarketTypes} from "filecoin-solidity-api/contracts/v0.8/types/MarketTypes.sol";
import {CommonTypes} from "filecoin-solidity-api/contracts/v0.8/types/CommonTypes.sol";
import {CBOR} from "solidity-cborutils/contracts/CBOR.sol";

using CBOR for CBOR.CBORBuffer;

contract DealClient {
    struct DealRequest {
        bytes piece_cid;
        uint64 piece_size;
        bool verified_deal;
        string label;
        int64 start_epoch;
        int64 end_epoch;
        uint256 storage_price_per_epoch;
        uint256 provider_collateral;
        uint256 client_collateral;
    }

    DealRequest[] public dealRequests;
    mapping(bytes32 => uint256) public proposalIndex;

    event DealProposed(bytes32 indexed proposalId, bytes piece_cid);

    function makeDealProposal(DealRequest calldata deal) external returns (bytes32) {
        uint256 idx = dealRequests.length;
        dealRequests.push(deal);

        bytes32 proposalId = keccak256(abi.encodePacked(block.timestamp, msg.sender, idx));
        proposalIndex[proposalId] = idx;

        emit DealProposed(proposalId, deal.piece_cid);
        return proposalId;
    }

    function getDealRequest(bytes32 proposalId) public view returns (DealRequest memory) {
        return dealRequests[proposalIndex[proposalId]];
    }
}
