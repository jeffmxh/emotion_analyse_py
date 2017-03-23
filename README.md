## 在Python中利用情感词典进行情感分析

注：此情感词典经过由新闻语料训练的word2vec进行扩充，并且识别了句子中的强调词以及否定词

### 使用方法：

将待处理的文件放入**raw_data**文件夹，调用脚本时输入要处理的文件名，需要处理的列，输出的文件名即可，脚本会自动在**raw_data**下生成一个**output**文件夹用于存放处理结果

```bash
python3 Jeffmxh_sentiment_analyse.py -i 'infile' -o 'outfile' -c 'column'
```
如需要查看命令行参数可输入
```bash 
python3 Jeffmxh_sentiment_analyse.py -h
```
