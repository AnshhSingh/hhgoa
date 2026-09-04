// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ContentVerifier {
    struct Registration {
        bytes32 contentHash;
        string sourceUrl;
        uint256 timestamp;
        address submitter;
    }

    mapping(bytes32 => Registration) public registrations;

    event ContentRegistered(
        bytes32 indexed contentHash,
        string sourceUrl,
        uint256 timestamp,
        address submitter
    );

    error AlreadyRegistered(bytes32 contentHash);

    function registerContent(
        bytes32 contentHash,
        string calldata sourceUrl,
        uint256 timestamp
    ) external {
        if (registrations[contentHash].timestamp != 0) {
            revert AlreadyRegistered(contentHash);
        }

        registrations[contentHash] = Registration({
            contentHash: contentHash,
            sourceUrl: sourceUrl,
            timestamp: timestamp,
            submitter: msg.sender
        });

        emit ContentRegistered(contentHash, sourceUrl, timestamp, msg.sender);
    }

    function getRegistration(bytes32 contentHash) external view returns (Registration memory) {
        return registrations[contentHash];
    }
}
