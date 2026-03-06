from pygrace.cli import main


def test_main_rejects_more_bxy_specs_than_files(capsys):
    rc = main(["-nxy", "a.dat", "-bxy", "1:2", "-bxy", "1:2"])
    captured = capsys.readouterr()

    assert rc == 2
    assert "more -bxy specs than data files" in captured.err
