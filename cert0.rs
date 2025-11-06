mod witness {
    const ADMIN_OR_DELEGATE: Either<[u8; 64],[u8; 64]> =
        Left(0xb65fc8a465dc8f5cc8740005f76eff26a634258c487297ba40ff5aec879269ae96ffedde7aacda3cb27306ef3e69dbeed352c734005a867166a79cf58f1d313b);
}

mod param {
    const ALICE_PUBKEY: u256 =
        0x9bef8d556d80e43ae7e0becb3a7e6838b95defe45896ed6075bb9035d06c9964;
    const BOB_PUBKEY: u256 =
        0xe37d58a1aae4ba059fd2503712d998470d3a2522f7e2335f544ef384d2199e02;
	const CERTIFICATE_SCRIPT_HASH: u256 =
        0xe37d58a1aae4ba059fd2503712d998470d3a2522f7e2335f544ef384d2199e02;
}

fn checksig(pk: Pubkey, sig: Signature) {
    let msg: u256 = jet::sig_all_hash();
    jet::bip_0340_verify((pk, msg), sig);
}

fn admin_revoke_certificate(admin_sig: Signature) {
	assert!(jet::num_outputs(), 1);

	let maybe_fee_output: Option<u256> = jet::output_is_fee(0);
    match maybe_fee_output {
        Some(is_fee_output: bool) => {
            assert!(is_fee_output)
        }
        None => {
            assert!(false);
        }
    };

    checksig(param::ALICE_PUBKEY, admin_sig);
}

fn delegate_revoke_certificate(delegate_sig: Signature) {
	assert!(jet::num_outputs(), 1);

	let maybe_fee_output: Option<u256> = jet::output_is_fee(0);
    match maybe_fee_output {
        Some(is_fee_output: bool) => {
            assert!(is_fee_output)
        }
        None => {
            assert!(false);
        }
    };

	checksig(param::BOB_PUBKEY, delegate_sig);
}

fn main() {
    match witness::ADMIN_OR_DELEGATE {
        Left(admin_sig: Signature) => admin_revoke_certificate(admin_sig),
        Right(delegate_sig: Signature) => delegate_revoke_certificate(delegate_sig),
    }
}
