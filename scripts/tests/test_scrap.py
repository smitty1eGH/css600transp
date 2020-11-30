import pytest

@pytest.fixture
def x():
    return [1,2,3]

@pytest.fixture
def a():
    return ['a','b','c']

def test_this(x,a):
    for y in x:
        for b in a:
            print(f'{y}\t{b}')
