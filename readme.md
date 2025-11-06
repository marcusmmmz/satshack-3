git clone --branch 2025-10/pset-signer https://github.com/apoelstra/hal-simplicity.git

# Build

cargo build --release

# Install as hal-simplicity (replaces any older version)

cp target/release/hal-simplicity ~/.cargo/bin/hal-simplicity

# Verify

hal-simplicity --version
hal-simplicity simplicity pset --help
