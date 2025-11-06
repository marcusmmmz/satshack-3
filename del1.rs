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

fn admin_spend(admin_sig: Signature) {
    checksig(param::ALICE_PUBKEY, admin_sig);
}

fn delegate_spend(delegate_sig: Signature) {
	assert!(jet::num_outputs(), 3);

    let self_hash: u256 = jet::current_script_hash();

    let maybe_hash_self: Option<u256> = jet::output_script_hash(0);
    match maybe_hash_self {
        Some(out_hash: u256) => {
            assert!(jet::eq_256(self_hash, out_hash));
        }
        None => {
            assert!(false);
        }
    };

	let maybe_hash_certificate: Option<u256> = jet::output_script_hash(1);
    match maybe_hash_certificate {
        Some(out_hash: u256) => {
            assert!(jet::eq_256(param::CERTIFICATE_SCRIPT_HASH, out_hash));
        }
        None => {
            assert!(false);
        }
    };


	let maybe_fee_output: Option<u256> = jet::output_is_fee(2);
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
        Left(admin_sig: Signature) => admin_spend(admin_sig),
        Right(delegate_sig: Signature) => delegate_spend(delegate_sig),
    }
}
