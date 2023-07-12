import hepfile as m

def test_version():

    assert m._PANDAS
    assert m._AWKWARD
    assert m.__version__
