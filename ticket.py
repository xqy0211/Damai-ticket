#!/usr/bin/env python
# -*- coding:utf-8 -*-
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from time import sleep
import re
from tkinter import *
import time
import pickle
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#具体票大麦网址
damai_url = "https://detail.damai.cn/item.htm?spm=a2oeg.search_category.0.0.30664d15mB8an2&id=598610277762&clicktitle=%E5%91%A8%E6%9D%B0%E4%BC%A62019%E5%98%89%E5%B9%B4%E5%8D%8E%E4%B8%96%E7%95%8C%E5%B7%A1%E5%9B%9E%E6%BC%94%E5%94%B1%E4%BC%9A%20%E5%8D%97%E4%BA%AC%E7%AB%99"  #改1
#大麦主页用来登陆的，更新cookies
login_url = "https://passport.damai.cn/login?ru=https%3A%2F%2Fwww.damai.cn%2F"

class Concert(object):
    def __init__(self, name, date, price, place, real_name, method=1):
        self.name = name  # 歌星
        self.date = date  # 日期序号优先级，比如，如果第二个时间可行，就选第二个，不然就选其他,最终只选一个
        self.price = price  # 票价序号优先级,道理同上
        self.place = place  # 地点
        self.status = 0  # 状态,表示如今进行到何种程度
        self.login_method = method  # {0:模拟登录,1:Cookie登录}自行选择登录方式
        self.real_name = real_name  # 实名者序号
        with open('./user_info.txt', 'r') as f:  # 读入用户名与密码和昵称
            self.uid = f.readline().strip('\n').strip('\r\n').strip()
            self.upw = f.readline().strip('\n').strip('\r\n').strip()
            self.usr_name = f.readline().strip('\n').strip('\r\n').strip()

    def enter_concert(self):
        print('###打开浏览器，进入大麦网###')
        self.driver = webdriver.Chrome()  # Chrome
        self.login()  # 先登录再说
        self.driver.refresh()
        try:
            #locator = (By.XPATH, "/html/body/div[1]/div/div[3]/div[1]/a[2]/div")
            locator = (By.XPATH, "/html/body/div[1]/div/div[3]/div[1]/a[2]/div")
            element = WebDriverWait(self.driver, 3).until(EC.text_to_be_present_in_element(locator, self.usr_name))
            self.status = 1
            print("###登录成功###")
        except:
            self.status = 0
            print("###登录失败###")

    def login(self):
        if self.login_method == 0:
            self.driver.get(login_url)  # 载入登录界面
            print('###开始登录###')
            try:
                element = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, 'alibaba-login-box')))
            except:
                print('###定位不到登录框###')
            self.driver.switch_to.frame('alibaba-login-box')  # 里面这个是iframe的id
            self.driver.find_element_by_id('fm-login-id').send_keys(self.uid)
            self.driver.find_element_by_id('fm-login-password').send_keys(self.upw)
            self.driver.find_element_by_tag_name("button").click()
        elif self.login_method == 1:
            if not os.path.exists('cookies.pkl'):  # 如果不存在cookie.pkl,就获取一下
                self.get_cookie()
            else:
                self.driver.get(damai_url)
                self.set_cookie()

    def get_cookie(self):
        self.driver.get(damai_url)
        print("###请点击登录###")
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:
            sleep(1)
        print("###请扫码登录###")
        while self.driver.title == '大麦登录':
            sleep(1)
        print("###扫码成功###")
        pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
        print("###Cookie保存成功###")

    def set_cookie(self):
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))  # 载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain': '.damai.cn',  # 必须有，不然就是假登录
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    "expires": "",
                    'path': '/',
                    'httpOnly': False,
                    'HostOnly': False,
                    'Secure': False}
                self.driver.add_cookie(cookie_dict)
            print('###载入Cookie###')
        except Exception as e:
            print(e)

    def choose_ticket(self):
        if self.status == 1:
            time_start = time.time()
            self.num = 1
            price = None
            plus = None
            while self.driver.title.find('确认订单') == -1:
                if self.num != 1:
                    self.driver.get(damai_url)
                self.driver.find_element_by_class_name('buybtn').click()#.find_element_by_link_text('立即预定').click()
                self.status = 2
                self.num += 1
            time_end = time.time()
            print("###经过%d轮奋斗，共耗时%f秒，抢票成功！请确认订单信息###" % (self.num - 1, round(time_end - time_start, 3)))

            #print(self.driver.find_elements_by_css_selector('input[type=checkbox]'))

    def check_order(self):
        if self.status == 2:
            print('###开始确认订单###')
            print('###默认购票人信息###')
            try:
                sleep(0.1)
                self.driver.find_element_by_xpath('//*[@id="confirmOrder_1"]/div[2]/div[2]/div[1]/div/label/span[1]/input').click()
            except:
                self.driver.find_element_by_xpath('//*[@id="confirmOrder_1"]/div[2]/div[2]/div[1]/div/label/span[1]/input').click()
            print('###同意以上协议并提交订单###')
            try:
                self.driver.find_element_by_xpath('//*[@id="confirmOrder_1"]/div[9]/button').click()  # 同意以上协议并提交订单
            except:
                self.driver.find_element_by_xpath('//*[@id="confirmOrder_1"]/div[9]/button').click()  # 同意以上协议并提交订单
            try:
                element = WebDriverWait(self.driver, 5).until(EC.title_contains('支付'))
                self.status = 3
                print('###成功提交订单,请手动支付###')
            except:
                print('###提交订单失败,请查看问题###')

    def finish(self):
        self.driver.quit()


if __name__ == '__main__':
    try:
        con = Concert('周杰伦', [1], [2], '南京', 1)  # 具体如果填写请查看类中的初始化函数
        con.enter_concert()
        con.choose_ticket()
        con.check_order()
    except:
        con.status = 1
        con.choose_ticket()
        con.check_order()

