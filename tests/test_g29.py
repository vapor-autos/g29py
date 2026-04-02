
"""
These are sanity checks meant to be checked manually.
time.sleep() is used to allow the user to see the effects of the commands.  
"""

import time

from g29py import G29


def test_init():
    g29 = None
    try:
        g29 = G29()
    except:
        assert False
    finally:
        assert g29 is not None
        assert g29.state is not None
        assert g29.cache is None
        
# test a few reads

def test_read():
    g29 = G29()
    dat = g29.read()
    assert dat is not None

def test_reset():
    g29 = G29()
    assert g29 is not None
    g29.reset()
    assert True # did not throw

# WRITE

def test_force_off():
    g29 = G29()
    g29.force_off(0xf3)
    assert True # did not throw

def test_set_friction():
    g29 = G29()
    g29.set_friction(0.5)
    assert True # did not throw
    time.sleep(5)
    g29.force_off(0xf3)
    assert True # did not throw

def test_set_range():
    g29 = G29()
    g29.set_range(500)
    assert True # did not throw
    time.sleep(5)
    g29.set_range(900) # set back to full range
    assert True # did not throw

def test_set_autocenter():
    g29 = G29()
    g29.set_autocenter(0.5, 0.5)
    assert True # did not throw
    time.sleep(5)
    g29.autocenter_off()
    assert True # did not throw

# def test_force_constant():
#     g29 = G29()
#     # g29.connect()
#     g29.force_constant(0.7)

# READ
# def test_pump():
#     g29 = G29()
#     dat = g29.pump()
#     print(dat)
#     assert True # did not throw
#     assert g29.cache is not None
#     print(g29.cache)
