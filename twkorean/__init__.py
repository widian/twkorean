# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Jaepil Jeong

import os
import imp

from collections import namedtuple

import jpype

from .escape import to_unicode, to_utf8, unicode_type


def _init_jvm():
    if not jpype.isJVMStarted():
        jars = []
        for top, dirs, files in os.walk(imp.find_module("twkorean")[1] + "/data/lib"):
            for nm in files:
                jars.append(os.path.join(top, nm))
        jpype.startJVM(jpype.getDefaultJVMPath(),
                       "-Djava.class.path=%s" % os.pathsep.join(jars))

_init_jvm()

_TwitterKoreanProcessorJava = jpype.JClass(
    "com.twitter.penguin.korean.TwitterKoreanProcessorJava")
KoreanToken = namedtuple("KoreanToken", ["text", "pos", "unknown"])
KoreanSegment = namedtuple("KoreanSegment", ["start", "length", "token"])
KoreanSegmentWithText = namedtuple("KoreanSegmentWithText", ["text", "segments"])
StemmedTextWithTokens = namedtuple("StemmedTextWithTokens", ["text", "tokens"])


class TwitterKoreanProcessor(object):
    _normalization = True
    _stemming = True
    def __init__(self, normalization=True, stemming=True):
        super(TwitterKoreanProcessor, self).__init__()

        self._processor = _TwitterKoreanProcessorJava
        self._normalization = normalization
        self._stemming = stemming

    def normalize(self, text):
        encode = lambda t: jpype.java.lang.String(t) if isinstance(text, unicode_type)\
            else jpype.java.lang.String(to_unicode(t))
        decode = lambda t: t if isinstance(text, unicode_type) else to_utf8(t)
        normalize = lambda t: self._processor.normalize(t) if self._normalization\
            else t
        return decode(normalize(encode(text)))

    def stemming(self, tokens):
        encode = lambda t: jpype.java.lang.String(t) if isinstance(text, unicode_type)\
            else jpype.java.lang.String(to_unicode(t))
        decode = lambda t: t if isinstance(text, unicode_type) else to_utf8(t)
        stem = lambda t: self._processor.stem(t) if self._stemming\
                else t
        return stem(tokens)

    def tokenize(self, text):
        encode = lambda t: jpype.java.lang.String(t) if isinstance(text, unicode_type)\
            else jpype.java.lang.String(to_unicode(t))
        decode = lambda t: t if isinstance(text, unicode_type) else to_utf8(t)

        tokens = decode(self.stemming(self._processor.tokenize(encode(self.normalize(text)))))

        new_tokens = list()
        while not tokens.isEmpty():
            new_tokens.append(tokens.head())
            tokens = tokens.tail()

        return [
            KoreanToken(
                text=decode(t.text()), pos=decode(t.pos().toString()), unknown=t.unknown()
            ) for t in new_tokens 
        ]

    def tokenize_to_strings(self, text):
        encode = lambda t: jpype.java.lang.String(t) if isinstance(text, unicode_type)\
            else jpype.java.lang.String(to_unicode(t))
        decode = lambda t: t if isinstance(text, unicode_type) else to_utf8(t)
        
        tokens = self._processor.tokensToJavaStringList(
                    self.stemming(self._processor.tokenize(
                        encode(self.normalize(text)))))
        new_tokens = list()
        while not tokens.isEmpty():
            new_tokens.append(tokens.pop())
        return [decode(t) for t in new_tokens]

    def tokenize_with_index(self, text):
        encode = lambda t: jpype.java.lang.String(t) if isinstance(text, unicode_type)\
            else jpype.java.lang.String(to_unicode(t))
        decode = lambda t: t if isinstance(text, unicode_type) else to_utf8(t)

        result = []
        tokens = self._processor.tokenizeWithIndex(encode(text))
        for t in tokens:
            token = KoreanToken(text=decode(t.token().text()),
                                pos=decode(t.token().pos().toString()),
                                unknown=t.token().unknown())
            segment = KoreanSegment(start=t.start(), length=t.length(), token=token)
            result.append(segment)

        return result

    # def tokenize_with_index_with_stemmer(self, text):
    #     encode = lambda t: jpype.java.lang.String(t) if isinstance(text, unicode_type)\
    #         else jpype.java.lang.String(to_unicode(t))
    #     decode = lambda t: t if isinstance(text, unicode_type) else to_utf8(t)

    #     token = self._processor.tokenizeWithIndexWithStemmer(encode(text))
    #     segments = []
    #     for segment in token.segments():
    #         token = KoreanToken(text=decode(segment.token().text()),
    #                             pos=decode(segment.token().pos().toString()),
    #                             unknown=segment.token().unknown())
    #         segment = KoreanSegment(start=segment.start(), length=segment.length(), token=token)
    #         segments.append(segment)

    #     return KoreanSegmentWithText(text=decode(token.text()), segments=segments)
