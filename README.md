## 在Python中利用情感词典进行情感分析

[项目主页](https://jeffmxh.github.io/emotion_analyse_py/)

注：此情感词典经过由新闻语料训练的word2vec进行扩充，并且识别了句子中的强调词以及否定词

### 使用方法：

将待处理的文件放入**raw_data**文件夹，调用脚本时输入要处理的文件名，需要处理的列，输出的文件名即可，脚本会自动在**raw_data**下生成一个**output**文件夹用于存放处理结果

```bash
python3 Jeffmxh_sentiment_analyse.py -i 'infile' -c 'column' -n 16
```
### 参数说明：
1. ``-i``或``--inpath``：输入excel文件的名称
2. ``-c``或``--column``：输入数据要处理的列明
3. ``-n``或``--ncores``：处理是并行的线程数

如需要查看命令行参数可输入
```bash 
python3 Jeffmxh_sentiment_analyse.py -h
```

***

**致谢**：特别感谢[ALEX](https://github.com/alexwwang)以及南京巴兰塔信息科技有限公司在我完成此项目过程中对我的帮助以及技术支持！
