#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
import abc


class POC(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def check(self) -> bool:
        """
        检测是否存在相关漏洞
        """
        pass

    @abc.abstractmethod
    def info(self) -> dict:
        """
        返回本POC的所有信息
        """
        pass

