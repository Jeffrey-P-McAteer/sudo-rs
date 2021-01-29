

const HELP_TEXT: &'static str = r#"cvtsudoers - convert between sudoers file formats

usage: cvtsudoers [-ehMpV] [-b dn] [-c conf_file ] [-d deftypes] [-f output_format] [-i input_format] [-I increment] [-m filter] [-o output_file] [-O start_point] [-P padding] [-s sections] [input_file]

Options:
  -b, --base=dn              the base DN for sudo LDAP queries
  -c, --config=conf_file     the path to the configuration file
  -d, --defaults=deftypes    only convert Defaults of the specified types
  -e, --expand-aliases       expand aliases when converting
  -f, --output-format=format set output format: JSON, LDIF or sudoers
  -i, --input-format=format  set input format: LDIF or sudoers
  -I, --increment=num        amount to increase each sudoOrder by
  -h, --help                 display help message and exit
  -m, --match=filter         only convert entries that match the filter
  -M, --match-local          match filter uses passwd and group databases
  -o, --output=output_file   write converted sudoers to output_file
  -O, --order-start=num      starting point for first sudoOrder
  -p, --prune-matches        prune non-matching users, groups and hosts
  -P, --padding=num          base padding for sudoOrder increment
  -s, --suppress=sections    suppress output of certain sections
  -V, --version              display version information and exit

"#;


fn main() {
    use std::env;
    // Brutalist check for --help, this will get designed better as we add cli parsing
    for argument in env::args() {
        if &argument == "--help" {
          println!("{}", HELP_TEXT);
          return;
        }
    }

    println!("Hello, world!");
}
