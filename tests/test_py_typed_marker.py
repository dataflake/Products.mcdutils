def test_py_typed_marker_exists():
    import pathlib
    import Products.mcdutils as pkg

    root = pathlib.Path(pkg.__file__).parent
    assert (root / "py.typed").exists()
