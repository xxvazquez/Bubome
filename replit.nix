{pkgs}: {
  deps = [
    pkgs.borgbackup
    pkgs.zlib
    pkgs.c-ares
    pkgs.rustc
    pkgs.openssl
    pkgs.libxcrypt
    pkgs.libiconv
    pkgs.cargo
    pkgs.pkg-config
    pkgs.libffi
    pkgs.cacert
    pkgs.grpc
  ];
}
