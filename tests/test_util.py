from iwallpaper.util import hashsum


def test_hashsum():
    got = hashsum(b'hello')
    assert got == '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'