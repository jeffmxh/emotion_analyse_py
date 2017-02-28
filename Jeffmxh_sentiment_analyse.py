# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 15:12:46 2017

@author: Jeffmxh
"""

import pandas as pd
import numpy as np
import argparse
import logging
import re
import jieba 
import os
from os import path


'''
微博文本过滤
'''

def re_sub(text_l):
    '替换文本中的超链接和多余的空格'
    if isinstance(text_l, str) and (text_l is not None):
        text_s = re.sub('\s+', ' ', text_l)
        text_s = re.sub(' ', ',', text_s)
        text_s = re.sub('#.+?#|\[.+?]|【.+?】', '', text_s)
        text_s = re.sub('https?:[a-zA-Z\\/\\.0-9_]+', '', text_s)
        text_s = re.sub('@.+?[,，：:\ )]|@.+?$', '', text_s)
        text_s = re.sub('我在(\\w){0,2}[:：](\\w*)', '', text_s)
        text_s = re.sub('\\[(\\w){1,4}\\]', '', text_s)
        text_s = re.sub('&[a-z]+;', '', text_s)
    else:
        text_s = str(text_l)
        text_s = re_sub(text_s)
    return text_s


'''
把每一条评论分割成单独的句子
'''

def sentence_split(content):
    sentence = str(content)
    sentence = re.sub('\u200b', '', sentence)
    result = re.split('。|？|！|\\.|\\?|\\!', sentence)
    return [ele for ele in result if len(ele)>1]


'''
用于分词的类
'''

class jieba4null():
    """
    docstring for parser_word
    deal处理文本，返回词表、词性及依存关系三个值
    """
    def __init__(self,n_core = 16):
        self.rootdir = os.getcwd()
        self.STOP_WORDS_LIST = self.load_txt(path.join(self.rootdir, 'stopwords_utf8.txt'))
        self.STOP_WORDS_LIST = set([re.sub('\n', '', item) for item in self.STOP_WORDS_LIST])
        jieba.load_userdict(path.join(self.rootdir, 'emotion_user_dict.txt'))
        self.n_CORE=n_core
        jieba.enable_parallel(self.n_CORE-1)
    def filter_stop(self,input_text):
        for token in input_text:
            if token not in self.STOP_WORDS_LIST:
                yield token
    def cut_word(self,sent):
        words = self.filter_stop(jieba.cut(sent, cut_all=False))
        #words = jieba.cut(sent, cut_all=False)
        result = list(words)
        return list(filter(lambda x:x!='\u200b', result))
    def cut_sentence(self, sent_list):
        result = []
        for sent in sent_list:
            result.append(list(self.cut_word(sent)))
        return result
    def load_txt(self,file):
        with open(file,'r',encoding = 'utf-8') as f_h:
            res = [line.encode('utf-8', 'ignore').decode('utf-8', 'ignore') for line in f_h]
            return res


class polar_classifier():
    '''
    用于对句子列表进行极性分析的类
    '''
    def __init__(self):
        self.rootdir = os.getcwd()
        self.pos_list = self.load_txt(path.join(self.rootdir, 'full_pos_dict_sougou.txt'))
        self.neg_list = self.load_txt(path.join(self.rootdir, 'full_neg_dict_sougou.txt'))
        self.degree_dict = pd.read_excel(path.join(self.rootdir, 'degree_dict.xlsx'))
        self.deny_dict = ['不', '不是', '没有']
    def load_txt(self,file):
        with open(file,'r',encoding = 'utf-8') as f_h:
            res = [line.encode('utf-8', 'ignore').decode('utf-8', 'ignore') for line in f_h]
            result = [re.sub('\n', '', item) for item in res]
            return result
        
    # 鉴定词汇的情感极性，输入词汇以及正负列表

    def word_polar_classify(self, word, pos_list, neg_list):
        if word in pos_list:
            return 1
        elif word in neg_list:
            return -1
        else:
            return 0

    # 鉴定程度副词，degree:1~6
    
    def word_strength_classify(self, word, degree_dict):
        sub_dict = degree_dict.loc[degree_dict.word==word,:]
        if sub_dict.shape[0]==0:
            return 0
        else:
            return sub_dict.iloc[0,1]

    # 鉴定否定词

    def word_deny_classify(self, word, deny_dict):
        if word in deny_dict:
            return -1
        else:
            return 1
        
    # 分析单个列表词汇
    
    def single_list_classify(self, seg_list):
        sign = 1
        k = 1
        result_list = []
        for i,word in enumerate(seg_list):
            polar_temp = self.word_polar_classify(word, self.pos_list, self.neg_list)
            if polar_temp!=0:
                result_temp = polar_temp * sign * k
                result_list.append(result_temp)
            else:
                sign *= self.word_deny_classify(word, self.deny_dict)
                k += self.word_strength_classify(word, self.degree_dict)
        if len(result_list)==0:
            return 'None'
        else:
            return sum(result_list)
        
    # 分析多个列表词汇
    
    def multi_list_classify(self, big_seg_list):
        res = []
        for seg_list in big_seg_list:
            res.append(self.single_list_classify(seg_list))
        senti_list = [x for x in res if x!='None']
        if len(senti_list)==0:
            return 'None'
        else:
            return sum(senti_list)


def main(path_to_data, column_to_deal, output_file):
    data = pd.read_excel(path_to_data)
    print('-----------------------------Data loaded!-----------------------------')
    re_sub_vec = np.vectorize(re_sub) # 函数向量化
    data[column_to_deal] = re_sub_vec(data[column_to_deal])
    print('-----------------------------Useless words trimmed!-----------------------------')
    data['content_list'] = data[column_to_deal].map(sentence_split)
    seg_word = jieba4null()
    data.loc[:,'seg_words'] = data['content_list'].map(seg_word.cut_sentence)
    print('-----------------------------Words segmentation finished!-----------------------------')
    worker = polar_classifier()
    data['polar'] = data['seg_words'].map(worker.multi_list_classify)
    print('-----------------------------Start writing to excel!-----------------------------')
    writer = pd.ExcelWriter(output_file)
    data.to_excel(writer, sheet_name='sheet1', encoding='utf-8', index=False)
    writer.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='情感极性分析脚本说明')
    parser.add_argument('-i', '--inpath', dest='input_path', nargs='?', default='',
                        help='Path to the input excel file.')
    parser.add_argument('-o', '--outpath', dest='output_path', nargs='?', default='emotion_result.xlsx',
                        help='Path to the output excel file.')
    parser.add_argument('-c', '--column', dest='column', nargs='?', default='content',
                        help='Specify the column name of doc content. Default is "content".')
    args = parser.parse_args()
    print('输入文件：' + str(args.input_path) + '\n输出文件：' + str(args.output_path) + '\n处理的列：' + str(args.column))
    main(path_to_data = args.input_path, column_to_deal = args.column, output_file = args.output_path)
