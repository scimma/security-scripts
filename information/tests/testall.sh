#!/bin/bash

source shunit2.sh

test_pydoc() {
  cd ../bin
  for py in *.py ; do pydoc `basename $py` ; done
    }

test_true() {
    return 0
}