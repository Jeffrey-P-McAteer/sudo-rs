
# Sudo-rs

`sudo` is an OS utility that allows unprivileged users to temporarily
execute privileged commands. The authoritative copy is developed at https://www.sudo.ws/sudo/,
but looking at [the source code](https://github.com/sudo-project/sudo) and
[safety issues](https://www.sudo.ws/security.html) it is clear the code needs a violent refresh.

One of the reasons for `sudo`s sprawling complexity is it's use in business processes - `sudo`
has plugins which enable [LDAP integration](https://www.sudo.ws/man/1.8.17/sudoers.ldap.man.html) and
[advanced syslog capabilities](https://www.sudo.ws/man/1.9.2/sudo_logsrvd.conf.man.html).

Sudo-rs aims to replace sudo without removing features or changing the configuration format in any way.

# Goals

 - [ ] Compile a `sudo` binary
 - [ ] Compile various library `.so` objects which live in `/usr/lib/sudo/`
    - These must provide an identical interface such that the old version of `sudo` can use them.
      Likewise, the new `sudo` binary must be able to load an old version of `/usr/lib/sudo/sudoers.so`.
 - [ ] Write some python scripts to compare implementations using `nspawn` containers.

At this point the ongoing goal is to follow the upstream `sudo` project and maintain
feature parity while not using unsafe practices which lead to common safety bugs.

Another small goal may be to track packaging scripts for common OSes like debian, fedora, Arch Linux, and Gentoo.

We can probably copy the original `sudo` manpages verbatim and track upstream changes; the binaries should
appear identical to end users (same config syntax, same CLI arguments).


# Project Organization

The upstream `sudo` repository is a mess and I can't even build `master` with `./configure && make` (as of 2021-01-28.

In light of the fact that `sudo` builds plugins as `.so` objects and packages commonly ship multiple
binaries (`sudo`, `cvtsudoers`, `sudo_logsrvd`, `sudo_sendlog`, `sudoedit`, `sudoreplay`, and `visudo` on my OS)
our `Cargo.toml` will declare multiple `[[bin]]` and `[[sublib]]` outputs. The sources for each of these outputs will be under `src/<bin-name>/main.rs` or `src/<lib-name>/lib.rs`.

I encourage downstream maintainers to follow this pattern; if your business has a custom `sudo` plugin called `libAuthenticateCustomers.so` and you want to upstream it to this repository then implement it in `src/AuthenticateCustomers/lib.rs` and add a corresponding `[[sublib]]` section to `Cargo.toml`.

# Building

This project uses a standard Cargo setup, the biggest differences being that
we are building multiple binaries and library outputs crate instead of a single one.
This happens by setting up a [cargo workspace](https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html)
for each binary and library.

To build everything for your OS:

```bash
cargo build
# For release binaries
cargo build --release
# Outputs go to target/debug/ or target/release/
```

# Plugins & Extensions

To create a new binary workspace:

```bash
cargo new my-binary-name --bin
# add "my-binary-name" to Cargo.toml in the members array
```

To create a new shared library workspace:

```bash
cargo new my-lib-name --lib
# Edit my-lib-name/Cargo.toml and add
#   crate_type = ["dylib"]
# under [lib]

# Add "my-lib-name" to Cargo.toml in the members array
```


