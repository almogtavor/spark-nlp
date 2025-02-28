#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Contains the Annotation data format
"""

from pyspark.sql.types import *


class Annotation:
    """Represents the output of Spark NLP Annotators and their details

    Parameters
    ----------
    annotator_type : str
        The type of the output of the annotator.
        Possible values are ``DOCUMENT, TOKEN, WORDPIECE,
        WORD_EMBEDDINGS, SENTENCE_EMBEDDINGS, CATEGORY, DATE, ENTITY, SENTIMENT, POS, CHUNK, NAMED_ENTITY,
        NEGEX, DEPENDENCY, LABELED_DEPENDENCY, LANGUAGE, KEYWORD, DUMMY``.
    begin : int
        The index of the first character under this annotation.
    end : int
        The index of the last character under this annotation.
    result : str
        The resulting string of the annotation.
    metadata : dict
        Associated metadata for this annotation
    embeddings : list
        Embeddings vector where applicable
    """

    def __init__(self, annotator_type, begin, end, result, metadata, embeddings):
        self.annotator_type = annotator_type
        self.begin = begin
        self.end = end
        self.result = result
        self.metadata = metadata
        self.embeddings = embeddings

    def copy(self, result):
        """Creates new Annotation with a different result, containing all settings of this Annotation.

        Parameters
        ----------
        result : str
            The result of the annotation that should be copied.

        Returns
        -------
        Annotation
            Newly created Annotation
        """
        return Annotation(self.annotator_type, self.begin, self.end, result, self.metadata, self.embeddings)

    def __str__(self):
        return "Annotation(%s, %i, %i, %s, %s)" % (
            self.annotator_type,
            self.begin,
            self.end,
            self.result,
            str(self.metadata)
        )

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def dataType():
        """Returns a Spark :class:`StructType`, that represents the schema of the Annotation.

        Returns
        -------
        StructType
            Spark Schema of the Annotation
        """
        return StructType([
            StructField('annotatorType', StringType(), False),
            StructField('begin', IntegerType(), False),
            StructField('end', IntegerType(), False),
            StructField('result', StringType(), False),
            StructField('metadata', MapType(StringType(), StringType()), False),
            StructField('embeddings', ArrayType(FloatType()), False)
        ])

    @staticmethod
    def arrayType():
        """Returns a Spark :class:`ArrayType`, that contains the :func:`dataType` of the annotation.

        Returns
        -------
        ArrayType
            ArrayType with the Annotation data type.
        """
        return ArrayType(Annotation.dataType())

    @staticmethod
    def fromRow(row):
        """Creates a Annotation from a Spark :class:`Row`.

        Parameters
        ----------
        row : Row
            Spark row containing columns for ``annotatorType, begin, end, result, metadata, embeddings``.

        Returns
        -------
        Annotation
            The new Annotation.
        """
        return Annotation(row.annotatorType, row.begin, row.end, row.result, row.metadata, row.embeddings)

    @staticmethod
    def toRow(annotation):
        """Transforms an Annotation to a Spark :class:`Row`.

        Parameters
        ----------
        annotation : Annotation
            The Annotation to be transformed.

        Returns
        -------
        Row
            The new Row.
        """
        from pyspark.sql import Row
        return Row(annotation.annotator_type, annotation.begin, annotation.end, annotation.result, annotation.metadata, annotation.embeddings)


