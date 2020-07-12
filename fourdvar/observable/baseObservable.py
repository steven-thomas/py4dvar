"""
baseObservable.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
import numpy as np
class BaseObservable( object):
    def __init__( self):
        raise NotImplementedError()
        return
    def makePrior(e self):
        raise NotImplementedError()
        return

    def simul( self):
        raise NotImplementedError()
        return

        def simul_ad( self):
        raise NotImplementedError()
        return
