# from anyascii import anyascii
# import urllib
# #
# content = "https%3A/lh3.googleusercontent.com/a/ACg8ocLulocd8Rxb3wx8VBZrU9PMYmxDv2zf33-4aDDP4dve%3Ds96-c"
# a=bytes(content, 'utf-8')

# decoded_string = a.decode('utf-8')
# # q=content.encode('cp1252').decode('utf8')
# # print(q)
# # a=urllib.parse.unquote(content)
# print(decoded_string)


# # from unidecode import unidecode
# # unidecode(yourStringtoDecode)

# import codecs

# # unicode string to be converted
# u_string = 'https%3A/lh3.googleusercontent.com/a/ACg8ocLulocd8Rxb3wx8VBZrU9PMYmxDv2zf33-4aDDP4dve%3Ds96-c'

# # encoding the unicode string to byte string
# b_string = codecs.encode(u_string, 'utf-8')

# print(b_string)


from urllib.parse import unquote
a='https%3A/lh3.googleusercontent.com/a/ACg8ocLulocd8Rxb3wx8VBZrU9PMYmxDv2zf33-4aDDP4dve%3Ds96-c'
url = unquote(a)
print(url)