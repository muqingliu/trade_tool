from __future__ import unicode_literals
#!/usr/bin/python
# -*- coding: utf8 -*-

def levenshtein(a,b):
    if not a : return 0
    if not b : return 0
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n

    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]


def similarity_count(base_string, compare_string):
    """简单计算两个字符串的相似度，考虑字符串的前后顺序
                 完全匹配，相似度是100，完全不同，相似度是0
    """
    if not isinstance(base_string, unicode):
        base_string = base_string.decode("utf8")
   
    if not isinstance(compare_string, unicode):
        compare_string = compare_string.decode("utf8")
       
    base_len = len(base_string)
    compare_len = len(compare_string)
   
    diff_len = levenshtein(base_string, compare_string)
    similar_count = compare_len - diff_len
    if similar_count < 0:
        similar_count = 0
   
    return similar_count * 100 / (base_len + compare_len - similar_count)