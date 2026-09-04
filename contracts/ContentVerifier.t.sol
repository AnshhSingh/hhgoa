// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// To run this test, you must have forge-std installed.
// Run: forge install foundry-rs/forge-std --no-commit
import "forge-std/Test.sol";
import "./ContentVerifier.sol";

contract ContentVerifierTest is Test {
    ContentVerifier public verifier;

    event ContentRegistered(
        bytes32 indexed contentHash,
        string sourceUrl,
        uint256 timestamp,
        address submitter
    );

    function setUp() public {
        verifier = new ContentVerifier();
    }

    function test_RegisterContent() public {
        bytes32 hash = keccak256("test fingerprint data");
        string memory url = "https://example.com/source";
        uint256 timestamp = block.timestamp;
        
        // We expect the exact event to be emitted
        vm.expectEmit(true, false, false, true);
        emit ContentRegistered(hash, url, timestamp, address(this));
        
        verifier.registerContent(hash, url, timestamp);
        
        // Retrieve and assert
        ContentVerifier.Registration memory reg = verifier.getRegistration(hash);
        assertEq(reg.contentHash, hash);
        assertEq(reg.sourceUrl, url);
        assertEq(reg.timestamp, timestamp);
        assertEq(reg.submitter, address(this));
    }

    function test_CannotRegisterDuplicate() public {
        bytes32 hash = keccak256("test duplicate data");
        
        verifier.registerContent(hash, "url1", 123);
        
        // Try registering the same hash again
        vm.expectRevert(abi.encodeWithSelector(ContentVerifier.AlreadyRegistered.selector, hash));
        verifier.registerContent(hash, "url2", 456);
    }
}
