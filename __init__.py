"""
提出時に必要になるinitファイルです．
MyAgentの部分を自分のエージェントクラスに変更してください．

提出時にはrequrements.txtも必要になります．
>>> pip freeze > requirements.txt
"""
from .Myagent import *

MAIN_AGENT = MyAgent
__all__ = MyAgent.__all__

__author__ = ""
__team__ = ""
__email__ = ""