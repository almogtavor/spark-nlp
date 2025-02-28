---
layout: docs
header: true
title: Spark NLP for Healthcare Release Notes
permalink: /docs/en/licensed_release_notes
key: docs-licensed-release-notes
modify_date: 2021-07-14
---


## 3.1.3
We are glad to announce that Spark NLP for Healthcare 3.1.3 has been released!.
This release comes with new features, new models, bug fixes, and examples.

#### Highlights
+ New Relation Extraction model and a Pretrained pipeline for extracting and linking ADEs
+ New Entity Resolver model for SNOMED codes
+ ChunkConverter Annotator
+ BugFix: getAnchorDateMonth method in DateNormalizer.
+ BugFix: character map in MedicalNerModel fine-tuning.

##### New Relation Extraction model and a Pretrained pipeline for extracting and linking ADEs

We are releasing a new Relation Extraction Model for ADEs. This model is trained using Bert Word embeddings (`biobert_pubmed_base_cased`), and is capable of linking ADEs and Drugs.

*Example*:

```python
re_model = RelationExtractionModel()\
        .pretrained("re_ade_biobert", "en", 'clinical/models')\
        .setInputCols(["embeddings", "pos_tags", "ner_chunks", "dependencies"])\
        .setOutputCol("relations")\
        .setMaxSyntacticDistance(3)\ #default: 0 
        .setPredictionThreshold(0.5)\ #default: 0.5 
        .setRelationPairs(["ade-drug", "drug-ade"]) # Possible relation pairs. Default: All Relations.

nlp_pipeline = Pipeline(stages=[documenter, sentencer, tokenizer, words_embedder, pos_tagger, ner_tagger, ner_chunker, dependency_parser, re_model])

light_pipeline = LightPipeline(nlp_pipeline.fit(spark.createDataFrame([['']]).toDF("text")))

text ="""Been taking Lipitor for 15 years , have experienced sever fatigue a lot!!! . Doctor moved me to voltaren 2 months ago , so far , have only experienced cramps"""

annotations = light_pipeline.fullAnnotate(text)
```

We also have a new pipeline comprising of all models related to ADE(Adversal Drug Event) as part of this release. This pipeline includes classification, NER, assertion and relation extraction models. Users can now use this pipeline to get classification result, ADE and Drug entities, assertion status for ADE entities, and relations between ADE and Drug entities.

Example:

```python
    pretrained_ade_pipeline = PretrainedPipeline('explain_clinical_doc_ade', 'en', 'clinical/models')
    
    result = pretrained_ade_pipeline.fullAnnotate("""Been taking Lipitor for 15 years , have experienced sever fatigue a lot!!! . Doctor moved me to voltaren 2 months ago , so far , have only experienced cramps""")[0]
```

*Results*:

```bash
Class: True

NER_Assertion:
|    | chunk                   | entitiy    | assertion   |
|----|-------------------------|------------|-------------|
| 0  | Lipitor                 | DRUG       | -           |
| 1  | sever fatigue           | ADE        | Conditional |
| 2  | voltaren                | DRUG       | -           |
| 3  | cramps                  | ADE        | Conditional |

Relations:
|    | chunk1                        | entitiy1   | chunk2      | entity2 | relation |
|----|-------------------------------|------------|-------------|---------|----------|
| 0  | sever fatigue                 | ADE        | Lipitor     | DRUG    |        1 |
| 1  | cramps                        | ADE        | Lipitor     | DRUG    |        0 |
| 2  | sever fatigue                 | ADE        | voltaren    | DRUG    |        0 |
| 3  | cramps                        | ADE        | voltaren    | DRUG    |        1 |

```
##### New Entity Resolver model for SNOMED codes

We are releasing a new SentenceEntityResolver model for SNOMED codes. This model also includes AUX SNOMED concepts and can find codes for Morph Abnormality, Procedure, Substance, Physical Object, and Body Structure entities. In the metadata, the `all_k_aux_labels` can be divided to get further information: `ground truth`, `concept`, and `aux` . In the example shared below the ground truth is `Atherosclerosis`, concept is `Observation`, and aux is `Morph Abnormality`.

*Example*:

```python
snomed_resolver = SentenceEntityResolverModel.pretrained("sbiobertresolve_snomed_findings_aux_concepts", "en", "clinical/models") \
     .setInputCols(["ner_chunk", "sbert_embeddings"]) \
     .setOutputCol("snomed_code")\
     .setDistanceFunction("EUCLIDEAN")

snomed_pipelineModel = PipelineModel(
    stages = [
        documentAssembler,
        sbert_embedder,
        snomed_resolver])

snomed_lp = LightPipeline(snomed_pipelineModel)
result = snomed_lp.fullAnnotate("atherosclerosis")

```

*Results*:

```bash
|    | chunks          | code     | resolutions                                                                                                                                                                                                                                                                                                                                                                                                                    | all_codes                                                                                                                                                                                          | all_k_aux_labels                                      | all_distances                                                                                                                                   |
|---:|:----------------|:---------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------|
|  0 | atherosclerosis | 38716007 | [atherosclerosis, atherosclerosis, atherosclerosis, atherosclerosis, atherosclerosis, atherosclerosis, atherosclerosis artery, coronary atherosclerosis, coronary atherosclerosis, coronary atherosclerosis, coronary atherosclerosis, coronary atherosclerosis, arteriosclerosis, carotid atherosclerosis, cardiovascular arteriosclerosis, aortic atherosclerosis, aortic atherosclerosis, atherosclerotic ischemic disease] | [38716007, 155382007, 155414001, 195251000, 266318005, 194848007, 441574008, 443502000, 41702007, 266231003, 155316000, 194841001, 28960008, 300920004, 39468009, 155415000, 195252007, 129573006] | 'Atherosclerosis', 'Observation', 'Morph Abnormality' | [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0280, 0.0451, 0.0451, 0.0451, 0.0451, 0.0451, 0.0462, 0.0477, 0.0466, 0.0490, 0.0490, 0.0485 |
```


##### ChunkConverter Annotator

Allows to use RegexMather chunks as NER chunks and feed the output to the downstream annotators like RE or Deidentification.

```python
document_assembler = DocumentAssembler().setInputCol('text').setOutputCol('document')

sentence_detector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")

regex_matcher = RegexMatcher()\
    .setInputCols("sentence")\
    .setOutputCol("regex")\
    .setExternalRules(path="../src/test/resources/regex-matcher/rules.txt",delimiter=",")

chunkConverter = ChunkConverter().setInputCols("regex").setOutputCol("chunk")
```


## 3.1.2
We are glad to announce that Spark NLP for Healthcare 3.1.2 has been released!.
This release comes with new features, new models, bug fixes, and examples.

#### Highlights
+ Support for Fine-tuning of Ner models.
+ More builtin(pre-defined) graphs for MedicalNerApproach.
+ Date Normalizer.
+ New Relation Extraction Models for ADE.
+ Bug Fixes.
+ Support for user-defined Custom Transformer.
+ Java Workshop Examples.
+ Deprecated Compatibility class in Python.


##### Support for Fine Tuning of Ner models

Users can now resume training/fine-tune existing(already trained) Spark NLP MedicalNer models on new data. Users can simply provide the path to any existing MedicalNer model and train it further on the new dataset:

```
ner_tagger = MedicalNerApproach().setPretrainedModelPath("/path/to/trained/medicalnermodel") 
```

If the new dataset contains new tags/labels/entities, users can choose to override existing tags with the new ones. The default behaviour is to reset the list of existing tags and generate a new list from the new dataset. It is also possible to preserve the existing tags by setting the 'overrideExistingTags' parameter:

```
ner_tagger = MedicalNerApproach()\
  .setPretrainedModelPath("/path/to/trained/medicalnermodel")\
  .setOverrideExistingTags(False)
```

Setting overrideExistingTags to false is intended to be used when resuming trainig on the same, or very similar dataset (i.e. with the same tags or with just a few different ones).

If tags overriding is disabled, and new tags are found in the training set, then the approach will try to allocate them to unused output nodes, if any. It is also possible to override specific tags of the old model by mapping them to new tags:


```bash
ner_tagger = MedicalNerApproach()\
  .setPretrainedModelPath("/path/to/trained/medicalnermodel")\
  .setOverrideExistingTags(False)\
  .setTagsMapping("B-PER,B-VIP", "I-PER,I-VIP")
```

In this case, the new tags `B-VIP` and `I-VIP` will replace the already trained tags `B-PER` and `I-PER`. Unmapped old tags will remain in use and unmapped new tags will be allocated to new outpout nodes, if any.

Jupyter Notebook: [Finetuning Medical NER Model Notebook](https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/1.5.Resume_MedicalNer_Model_Training.ipynb)

##### More builtin graphs for MedicalNerApproach

Seventy new TensorFlow graphs have been added to the library of available graphs which are used to train MedicalNer models. The graph with the optimal set of parameters is automatically chosen by MedicalNerApproach.


##### DateNormalizer

New annotator that normalize dates to the format `YYYY/MM/DD`.
This annotator identifies dates in chunk annotations, and transform these dates to the format `YYYY/MM/DD`.
Both the input and output formats for the annotator are `chunk`.

Example:


```bash
	sentences = [
		    ['08/02/2018'],
		    ['11/2018'],
		    ['11/01/2018'],
		    ['12Mar2021'],
		    ['Jan 30, 2018'],
		    ['13.04.1999'],
		    ['3April 2020'],
		    ['next monday'],
		    ['today'],
		    ['next week'],
	]
	df = spark.createDataFrame(sentences).toDF("text")
	document_assembler = DocumentAssembler().setInputCol('text').setOutputCol('document')
	chunksDF = document_assembler.transform(df)
	aa = map_annotations_col(chunksDF.select("document"),
				    lambda x: [Annotation('chunk', a.begin, a.end, a.result, a.metadata, a.embeddings) for a in x], "document",
				    "chunk_date", "chunk")
	dateNormalizer = DateNormalizer().setInputCols('chunk_date').setOutputCol('date').setAnchorDateYear(2021).setAnchorDateMonth(2).setAnchorDateDay(27)
	dateDf = dateNormalizer.transform(aa)
	dateDf.select("date.result","text").show()
```

```bash
     
+-----------+----------+
|text        |  date    |
+-----------+----------+
|08/02/2018  |2018/08/02|
|11/2018     |2018/11/DD|
|11/01/2018  |2018/11/01|
|12Mar2021   |2021/03/12|
|Jan 30, 2018|2018/01/30|
|13.04.1999  |1999/04/13|
|3April 2020 |2020/04/03|
|next Monday |2021/06/19|
|today       |2021/06/12|
|next week   |2021/06/19|
+-----------+----------+
```

##### New Relation Extraction Models for ADE

We are releasing new Relation Extraction models for ADE (Adverse Drug Event). This model is available in both `RelationExtraction` and Bert based `RelationExtractionDL` versions, and is capabale of linking drugs with ADE mentions.

Example

```bash
    ade_re_model = new RelationExtractionModel().pretrained('ner_ade_clinical', 'en', 'clinical/models')\
                                     .setInputCols(["embeddings", "pos_tags", "ner_chunk", "dependencies"])\
                                     .setOutputCol("relations")\
                                     .setPredictionThreshold(0.5)\
                                     .setRelationPairs(['ade-drug', 'drug-ade'])
    pipeline = Pipeline(stages=[documenter, sentencer, tokenizer, pos_tagger, words_embedder, ner_tagger, ner_converter, 
                                                   dependency_parser, re_ner_chunk_filter, re_model])
    text ="""A 30 year old female presented with tense bullae due to excessive use of naproxin, and leg cramps relating to oxaprozin."""

    p_model = pipeline.fit(spark.createDataFrame([[text]]).toDF("text"))
    
    result = p_model.transform(data)
       
```

Results
```bash
|    | chunk1        | entity1    |  chunk2       | entity2   |    result  |
|---:|:--------------|:-----------|:--------------|:----------|-----------:|
|  0 | tense bullae  | ADE        | naproxin      | DRUG      |          1 |
|  1 | tense bullae  | ADE        | oxaprozin     | DRUG      |          0 |
|  2 | naproxin      | DRUG       | leg cramps    | ADE       |          0 |
|  3 | leg cramps    | ADE        | oxaprozin     | DRUG      |          1 |

```

Benchmarking
Model: `re_ade_clinical`
```bash

              precision    recall  f1-score   support
           0       0.85      0.89      0.87      1670
           1       0.88      0.84      0.86      1673
   micro avg       0.87      0.87      0.87      3343
   macro avg       0.87      0.87      0.87      3343
weighted avg       0.87      0.87      0.87      3343
```

Model: `redl_ade_biobert`
```bash
Relation           Recall Precision        F1   Support
0                   0.894     0.946     0.919      1011
1                   0.963     0.926     0.944      1389
Avg.                0.928     0.936     0.932
Weighted Avg.       0.934     0.934     0.933
```

##### Bug Fixes
+ RelationExtractionDLModel had an issue(BufferOverflowException) on versions 3.1.0 and 3.1.1, which is fixed with this release.
+ Some pretrained RelationExtractionDLModels got outdated after release 3.0.3, new updated models were created, tested and made available to be used with versions 3.0.3, and later.
+ Some SentenceEntityResolverModels which did not work with Spark 2.4/2.3 were fixed.

##### Support for user-defined Custom Transformer.
Utility classes to define custom transformers in python are included in this release. This allows users to define functions in Python to manipulate Spark-NLP annotations. This new Transformers can be added to pipelines like any of the other models you're already familiar with.
Example how to use the custom transformer.

```python
        def myFunction(annotations):
            # lower case the content of the annotations
            return [a.copy(a.result.lower()) for a in annotations]

        custom_transformer = CustomTransformer(f=myFunction).setInputCol("ner_chunk").setOutputCol("custom")
        outputDf = custom_transformer.transform(outdf).select("custom").toPandas()
```

##### Java Workshop Examples

Add Java examples in the [workshop repository](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/java/healthcare).

##### Deprecated Compatibility class in Python

Due to active release cycle, we are adding & training new pretrained models at each release and it might be tricky to maintain the backward compatibility or keep up with the latest models and versions, especially for the users using our models locally in air-gapped networks.

We are releasing a new utility class to help you check your local & existing models with the latest version of everything we have up to date. You will not need to specify your AWS credentials from now on. This new class is now replacing the previous Compatibility class written in Python and CompatibilityBeta class written in Scala.

```        
from sparknlp_jsl.compatibility import Compatibility

compatibility = Compatibility(spark)

print(compatibility.findVersion('sentence_detector_dl_healthcare'))
```

Output
```
[{'name': 'sentence_detector_dl_healthcare', 'sparkVersion': '2.4', 'version': '2.6.0', 'language': 'en', 'date': '2020-09-13T14:44:42.565', 'readyToUse': 'true'}, {'name': 'sentence_detector_dl_healthcare', 'sparkVersion': '2.4', 'version': '2.7.0', 'language': 'en', 'date': '2021-03-16T08:42:34.391', 'readyToUse': 'true'}]
```


## 3.1.1
We are glad to announce that Spark NLP for Healthcare 3.1.1 has been released!

#### Highlights
+ MedicalNerModel new parameter `includeAllConfidenceScores`.
+ MedicalNerModel new parameter `inferenceBatchSize`.
+ New Resolver Models
+ Updated Resolver Models
+ Getting Started with Spark NLP for Healthcare Notebook in Databricks

#### MedicalNer new parameter `includeAllConfidenceScores`
You can now customize whether you will require confidence score for every token(both entities and non-entities) at the output of the MedicalNerModel, or just for the tokens recognized as entities.

#### MedicalNerModel new parameter `inferenceBatchSize`
You can now control the batch size used during inference as a separate parameter from the one you used during training of the model. This can be useful in the situation in which the hardware on which you run inference has different capacity. For example, when you have lower available memory during inference, you can reduce the batch size.
 
#### New Resolver Models
We trained three new sentence entity resolver models. 

+ `sbertresolve_snomed_bodyStructure_med` and `sbiobertresolve_snomed_bodyStructure` models map extracted medical (anatomical structures) entities to Snomed codes (body structure version). 

     + `sbertresolve_snomed_bodyStructure_med` : Trained  with using `sbert_jsl_medium_uncased` embeddings.
     + `sbiobertresolve_snomed_bodyStructure`  : Trained with using `sbiobert_base_cased_mli` embeddings.

*Example* :
```
documentAssembler = DocumentAssembler()\
      .setInputCol("text")\
      .setOutputCol("ner_chunk")
jsl_sbert_embedder = BertSentenceEmbeddings.pretrained('sbert_jsl_medium_uncased','en','clinical/models')\
      .setInputCols(["ner_chunk"])\
      .setOutputCol("sbert_embeddings")
snomed_resolver = SentenceEntityResolverModel.pretrained("sbertresolve_snomed_bodyStructure_med, "en", "clinical/models) \
      .setInputCols(["ner_chunk", "sbert_embeddings"]) \
      .setOutputCol("snomed_code")
snomed_pipelineModel = PipelineModel(
    stages = [
        documentAssembler,
        jsl_sbert_embedder,
        snomed_resolver])
snomed_lp = LightPipeline(snomed_pipelineModel)
result = snomed_lp.fullAnnotate("Amputation stump")
```

*Result*:
```bash
|    | chunks           | code     | resolutions                                                                                                                                                                                                                                  | all_codes                                                                                       | all_distances                                                               |
|---:|:-----------------|:---------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------|
|  0 | amputation stump | 38033009 | [Amputation stump, Amputation stump of upper limb, Amputation stump of left upper limb, Amputation stump of lower limb, Amputation stump of left lower limb, Amputation stump of right upper limb, Amputation stump of right lower limb, ...]| ['38033009', '771359009', '771364008', '771358001', '771367001', '771365009', '771368006', ...] | ['0.0000', '0.0773', '0.0858', '0.0863', '0.0905', '0.0911', '0.0972', ...] |
```
 +  `sbiobertresolve_icdo_augmented` : This model maps extracted medical entities to ICD-O codes using sBioBert sentence embeddings. This model is augmented using the site information coming from ICD10 and synonyms coming from SNOMED vocabularies. It is trained with a dataset that is 20x larger than the previous version of ICDO resolver. Given the oncological entity found in the text (via NER models like ner_jsl), it returns top terms and resolutions along with the corresponding ICD-10 codes to present more granularity with respect to body parts mentioned. It also returns the original histological behavioral codes and descriptions in the aux metadata.

*Example*:

```
...
chunk2doc = Chunk2Doc().setInputCols("ner_chunk").setOutputCol("ner_chunk_doc")
 
sbert_embedder = BertSentenceEmbeddings\
     .pretrained("sbiobert_base_cased_mli","en","clinical/models")\
     .setInputCols(["ner_chunk_doc"])\
     .setOutputCol("sbert_embeddings")
 
icdo_resolver = SentenceEntityResolverModel.pretrained("sbiobertresolve_icdo_augmented","en", "clinical/models") \
     .setInputCols(["ner_chunk", "sbert_embeddings"]) \
     .setOutputCol("resolution")\
     .setDistanceFunction("EUCLIDEAN")
nlpPipeline = Pipeline(stages=[document_assembler, sentence_detector, tokenizer, word_embeddings, clinical_ner, ner_converter, chunk2doc, sbert_embedder, icdo_resolver])
empty_data = spark.createDataFrame([[""]]).toDF("text")
model = nlpPipeline.fit(empty_data)
results = model.transform(spark.createDataFrame([["The patient is a very pleasant 61-year-old female with a strong family history of colon polyps. The patient reports her first polyps noted at the age of 50. We reviewed the pathology obtained from the pericardectomy in March 2006, which was diagnostic of mesothelioma. She also has history of several malignancies in the family. Her father died of a brain tumor at the age of 81. Her sister died at the age of 65 breast cancer. She has two maternal aunts with history of lung cancer both of whom were smoker. Also a paternal grandmother who was diagnosed with leukemia at 86 and a paternal grandfather who had B-cell lymphoma."]]).toDF("text"))
```

*Result*:

```
+--------------------+-----+---+-----------+-------------+-------------------------+-------------------------+
|               chunk|begin|end|     entity|         code|        all_k_resolutions|              all_k_codes|
+--------------------+-----+---+-----------+-------------+-------------------------+-------------------------+
|        mesothelioma|  255|266|Oncological|9971/3||C38.3|malignant mediastinal ...|9971/3||C38.3:::8854/3...|
|several malignancies|  293|312|Oncological|8894/3||C39.8|overlapping malignant ...|8894/3||C39.8:::8070/2...|
|         brain tumor|  350|360|Oncological|9562/0||C71.9|cancer of the brain:::...|9562/0||C71.9:::9070/3...|
|       breast cancer|  413|425|Oncological|9691/3||C50.9|carcinoma of breast:::...|9691/3||C50.9:::8070/2...|
|         lung cancer|  471|481|Oncological|8814/3||C34.9|malignant tumour of lu...|8814/3||C34.9:::8550/3...|
|            leukemia|  560|567|Oncological|9670/3||C80.9|anemia in neoplastic d...|9670/3||C80.9:::9714/3...|
|     B-cell lymphoma|  610|624|Oncological|9818/3||C77.9|secondary malignant ne...|9818/3||C77.9:::9655/3...|
+--------------------+-----+---+-----------+-------------+-------------------------+-------------------------+
```

 
#### Updated Resolver Models
We updated `sbiobertresolve_snomed_findings` and `sbiobertresolve_cpt_procedures_augmented` resolver models to reflect the latest changes in the official terminologies.

#### Getting Started with Spark NLP for Healthcare Notebook in Databricks
We prepared a new notebook for those who want to get started with Spark NLP for Healthcare in Databricks : [Getting Started with Spark NLP for Healthcare Notebook](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/databricks/python/healthcare_case_studies/Get_Started_Spark_NLP_for_Healthcare.ipynb) 

## 3.1.0
We are glad to announce that Spark NLP for Healthcare 3.1.0 has been released!
#### Highlights
+ Improved load time & memory consumption for SentenceResolver models.
+ New JSL Bert Models.
+ JSL SBert Model Speed Benchmark.
+ New ICD10CM resolver models.
+ New Deidentification NER models.
+ New column returned in DeidentificationModel
+ New Reidentification feature
+ New Deidentification Pretrained Pipelines
+ Chunk filtering based on confidence
+ Extended regex dictionary fuctionallity in Deidentification
+ Enhanced RelationExtractionDL Model to create and identify relations between entities across the entire document
+ MedicalNerApproach can now accept a graph file directly.
+ MedicalNerApproach can now accept a user-defined name for log file.
+ More improvements in Scaladocs. 
+ Bug fixes in Deidentification module.
+ New notebooks.



#### Sentence Resolver Models load time improvement
Sentence resolver models now have faster load times, with a speedup of about 6X when compared to previous versions.
Also, the load process now is more  memory friendly meaning that the maximum memory required during load time is smaller, reducing the chances of OOM exceptions, and thus relaxing hardware requirements.

#### New JSL SBert Models
We trained new sBert models in TF2 and fined tuned on MedNLI, NLI and UMLS datasets with various parameters to cover common NLP tasks in medical domain. You can find the details in the following table.

+ `sbiobert_jsl_cased`
+ `sbiobert_jsl_umls_cased`
+ `sbert_jsl_medium_uncased`
+ `sbert_jsl_medium_umls_uncased`
+ `sbert_jsl_mini_uncased`
+ `sbert_jsl_mini_umls_uncased`
+ `sbert_jsl_tiny_uncased`
+ `sbert_jsl_tiny_umls_uncased`

#### JSL SBert Model Speed Benchmark

| JSL SBert Model| Base Model | Is Cased | Train Datasets | Inference speed (100 rows) |
|-|-|-|-|-|
| sbiobert_jsl_cased | biobert_v1.1_pubmed | Cased | medNLI, allNLI| 274,53 |
| sbiobert_jsl_umls_cased | biobert_v1.1_pubmed | Cased | medNLI, allNLI, umls | 274,52 |
| sbert_jsl_medium_uncased | uncased_L-8_H-512_A-8 | Uncased | medNLI, allNLI| 80,40 |
| sbert_jsl_medium_umls_uncased | uncased_L-8_H-512_A-8 | Uncased | medNLI, allNLI, umls | 78,35 |
| sbert_jsl_mini_uncased | uncased_L-4_H-256_A-4 | Uncased | medNLI, allNLI| 10,68 |
| sbert_jsl_mini_umls_uncased | uncased_L-4_H-256_A-4 | Uncased | medNLI, allNLI, umls | 10,29 |
| sbert_jsl_tiny_uncased | uncased_L-2_H-128_A-2 | Uncased | medNLI, allNLI| 4,54 |
| sbert_jsl_tiny_umls_uncased | uncased_L-2_H-128_A-2 | Uncased | medNLI, allNL, umls | 4,54 |

#### New ICD10CM resolver models:
These models map clinical entities and concepts to ICD10 CM codes using sentence bert embeddings. They also return the official resolution text within the brackets inside the metadata. Both models are augmented with synonyms, and previous augmentations are flexed according to cosine distances to unnormalized terms (ground truths).

+ `sbiobertresolve_icd10cm_slim_billable_hcc`: Trained with classic sbiobert mli. (`sbiobert_base_cased_mli`)

Models Hub Page : https://nlp.johnsnowlabs.com/2021/05/25/sbiobertresolve_icd10cm_slim_billable_hcc_en.html

+ `sbertresolve_icd10cm_slim_billable_hcc_med`: Trained with new jsl sbert(`sbert_jsl_medium_uncased`)

Models Hub Page : https://nlp.johnsnowlabs.com/2021/05/25/sbertresolve_icd10cm_slim_billable_hcc_med_en.html


*Example*: 'bladder cancer' 
+ `sbiobertresolve_icd10cm_augmented_billable_hcc`

| chunks | code | all_codes | resolutions |all_distances | 100x Loop(sec) |
|-|-|-|-|-|-|
| bladder cancer | C679 | [C679, Z126, D090, D494, C7911] | [bladder cancer, suspected bladder cancer, cancer in situ of urinary bladder, tumor of bladder neck, malignant tumour of bladder neck] | [0.0000, 0.0904, 0.0978, 0.1080, 0.1281] | 26,9 |

+ ` sbiobertresolve_icd10cm_slim_billable_hcc`

| chunks | code | all_codes | resolutions |all_distances | 100x Loop(sec) |
| - | - | - | - | - | - |
| bladder cancer | D090 | [D090, D494, C7911, C680, C679] | [cancer in situ of urinary bladder [Carcinoma in situ of bladder], tumor of bladder neck [Neoplasm of unspecified behavior of bladder], malignant tumour of bladder neck [Secondary malignant neoplasm of bladder], carcinoma of urethra [Malignant neoplasm of urethra], malignant tumor of urinary bladder [Malignant neoplasm of bladder, unspecified]] | [0.0978, 0.1080, 0.1281, 0.1314, 0.1284] | 20,9 |

+ `sbertresolve_icd10cm_slim_billable_hcc_med`

| chunks | code | all_codes | resolutions |all_distances | 100x Loop(sec) |
| - | - | - | - | - | - |
| bladder cancer | C671 | [C671, C679, C61, C672, C673] | [bladder cancer, dome [Malignant neoplasm of dome of bladder], cancer of the urinary bladder [Malignant neoplasm of bladder, unspecified], prostate cancer [Malignant neoplasm of prostate], cancer of the urinary bladder] | [0.0894, 0.1051, 0.1184, 0.1180, 0.1200] | 12,8 | 

#### New Deidentification NER Models

We trained four new NER models to find PHI data (protected health information) that may need to be deidentified. `ner_deid_generic_augmented` and `ner_deid_subentity_augmented` models are trained with a combination of 2014 i2b2 Deid dataset and in-house annotations as well as some augmented version of them. Compared to the same test set coming from 2014 i2b2 Deid dataset, we achieved a better accuracy and generalisation on some entity labels as summarised in the following tables. We also trained the same models with `glove_100d` embeddings to get more memory friendly versions.    

+ `ner_deid_generic_augmented`  : Detects PHI 7 entities (`DATE`, `NAME`, `LOCATION`, `PROFESSION`, `CONTACT`, `AGE`, `ID`).

Models Hub Page : https://nlp.johnsnowlabs.com/2021/06/01/ner_deid_generic_augmented_en.html

| entity| ner_deid_large (v3.0.3 and before)|ner_deid_generic_augmented (v3.1.0)|
|--|:--:|:--:|
|   CONTACT| 0.8695|0.9592 |
|      NAME| 0.9452|0.9648 |
|      DATE| 0.9778|0.9855 |
|  LOCATION| 0.8755|0.923 |

+ `ner_deid_subentity_augmented`: Detects PHI 23 entities (`MEDICALRECORD`, `ORGANIZATION`, `DOCTOR`, `USERNAME`, `PROFESSION`, `HEALTHPLAN`, `URL`, `CITY`, `DATE`, `LOCATION-OTHER`, `STATE`, `PATIENT`, `DEVICE`, `COUNTRY`, `ZIP`, `PHONE`, `HOSPITAL`, `EMAIL`, `IDNUM`, `SREET`, `BIOID`, `FAX`, `AGE`)

Models Hub Page : https://nlp.johnsnowlabs.com/2021/06/01/ner_deid_subentity_augmented_en.html

|entity| ner_deid_enriched (v3.0.3 and before)| ner_deid_subentity_augmented (v3.1.0)|
|-------------|:------:|:--------:|
|     HOSPITAL| 0.8519| 0.8983 |
|         DATE| 0.9766| 0.9854 |
|         CITY| 0.7493| 0.8075 |
|       STREET| 0.8902| 0.9772 |
|          ZIP| 0.8| 0.9504 |
|        PHONE| 0.8615| 0.9502 |
|       DOCTOR| 0.9191| 0.9347 |
|          AGE| 0.9416| 0.9469 |

+ `ner_deid_generic_glove`: Small version of `ner_deid_generic_augmented` and detects 7 entities.
+ `ner_deid_subentity_glove`: Small version of `ner_deid_subentity_augmented` and detects 23 entities.

*Example*:

Scala
```scala
...
val deid_ner = MedicalNerModel.pretrained("ner_deid_subentity_augmented", "en", "clinical/models") \
      .setInputCols(Array("sentence", "token", "embeddings")) \
      .setOutputCol("ner")
...
val nlpPipeline = new Pipeline().setStages(Array(document_assembler, sentence_detector, tokenizer, word_embeddings, deid_ner, ner_converter))
model = nlpPipeline.fit(spark.createDataFrame([[""]]).toDF("text"))

val result = pipeline.fit(Seq.empty["A. Record date : 2093-01-13, David Hale, M.D., Name : Hendrickson, Ora MR. # 7194334 Date : 01/13/93 PCP : Oliveira, 25 -year-old, Record date : 1-11-2000. Cocke County Baptist Hospital. 0295 Keats Street. Phone +1 (302) 786-5227."].toDS.toDF("text")).transform(data)
```

Python
```bash
...
deid_ner = MedicalNerModel.pretrained("ner_deid_subentity_augmented", "en", "clinical/models") \
      .setInputCols(["sentence", "token", "embeddings"]) \
      .setOutputCol("ner")
...
nlpPipeline = Pipeline(stages=[document_assembler, sentence_detector, tokenizer, word_embeddings, deid_ner, ner_converter])
model = nlpPipeline.fit(spark.createDataFrame([[""]]).toDF("text"))

results = model.transform(spark.createDataFrame(pd.DataFrame({"text": ["""A. Record date : 2093-01-13, David Hale, M.D., Name : Hendrickson, Ora MR. # 7194334 Date : 01/13/93 PCP : Oliveira, 25 -year-old, Record date : 1-11-2000. Cocke County Baptist Hospital. 0295 Keats Street. Phone +1 (302) 786-5227."""]})))
```
*Results*:
```bash
+-----------------------------+-------------+
|chunk                        |ner_label    |
+-----------------------------+-------------+
|2093-01-13                   |DATE         |
|David Hale                   |DOCTOR       |
|Hendrickson, Ora             |PATIENT      |
|7194334                      |MEDICALRECORD|
|01/13/93                     |DATE         |
|Oliveira                     |DOCTOR       |
|25-year-old                  |AGE          |
|1-11-2000                    |DATE         |
|Cocke County Baptist Hospital|HOSPITAL     |
|0295 Keats Street.           |STREET       |
|(302) 786-5227               |PHONE        |
|Brothers Coal-Mine           |ORGANIZATION |
+-----------------------------+-------------+
``` 


#### New column returned in DeidentificationModel

DeidentificationModel now can return a new column to save the mappings between the mask/obfuscated entities and original entities.
This column is optional and you can set it up with the `.setReturnEntityMappings(True)` method. The default value is False.
Also, the name for the column can be changed using the following method; `.setMappingsColumn("newAlternativeName")`
The new column will produce annotations with the following structure,
```
Annotation(
  type: chunk, 
  begin: 17, 
  end: 25, 
  result: 47,
    metadata:{
        originalChunk -> 01/13/93  //Original text of the chunk
        chunk -> 0  // The number of the chunk in the sentence
        beginOriginalChunk -> 95 // Start index of the original chunk
        endOriginalChunk -> 102  // End index of the original chunk
        entity -> AGE // Entity of the chunk
        sentence -> 2 // Number of the sentence
    }
)
```

#### New Reidentification feature

With the new ReidetificationModel, the user can go back to the original sentences using the mappings columns and the deidentification sentences.

*Example:*

Scala

```scala
val redeidentification = new ReIdentification()
     .setInputCols(Array("mappings", "deid_chunks"))
     .setOutputCol("original")
```

Python

```scala
reDeidentification = ReIdentification()
     .setInputCols(["mappings","deid_chunks"])
     .setOutputCol("original")
```

#### New Deidentification Pretrained Pipelines
We developed a `clinical_deidentification` pretrained pipeline that can be used to deidentify PHI information from medical texts. The PHI information will be masked and obfuscated in the resulting text. The pipeline can mask and obfuscate `AGE`, `CONTACT`, `DATE`, `ID`, `LOCATION`, `NAME`, `PROFESSION`, `CITY`, `COUNTRY`, `DOCTOR`, `HOSPITAL`, `IDNUM`, `MEDICALRECORD`, `ORGANIZATION`, `PATIENT`, `PHONE`, `PROFESSION`,  `STREET`, `USERNAME`, `ZIP`, `ACCOUNT`, `LICENSE`, `VIN`, `SSN`, `DLN`, `PLATE`, `IPADDR` entities. 

Models Hub Page : [clinical_deidentification](https://nlp.johnsnowlabs.com/2021/05/27/clinical_deidentification_en.html)

There is also a lightweight version of the same pipeline trained with memory efficient `glove_100d`embeddings.
Here are the model names:
- `clinical_deidentification`
- `clinical_deidentification_glove`

*Example:*

Python:
```bash 
from sparknlp.pretrained import PretrainedPipeline
deid_pipeline = PretrainedPipeline("clinical_deidentification", "en", "clinical/models")

deid_pipeline.annotate("Record date : 2093-01-13, David Hale, M.D. IP: 203.120.223.13. The driver's license no:A334455B. the SSN:324598674 and e-mail: hale@gmail.com. Name : Hendrickson, Ora MR. # 719435 Date : 01/13/93. PCP : Oliveira, 25 years-old. Record date : 2079-11-09, Patient's VIN : 1HGBH41JXMN109286.")
```
Scala:
```scala
import com.johnsnowlabs.nlp.pretrained.PretrainedPipeline
val deid_pipeline = PretrainedPipeline("clinical_deidentification","en","clinical/models")

val result = deid_pipeline.annotate("Record date : 2093-01-13, David Hale, M.D. IP: 203.120.223.13. The driver's license no:A334455B. the SSN:324598674 and e-mail: hale@gmail.com. Name : Hendrickson, Ora MR. # 719435 Date : 01/13/93. PCP : Oliveira, 25 years-old. Record date : 2079-11-09, Patient's VIN : 1HGBH41JXMN109286.")
```
*Result*:
```bash
{'sentence': ['Record date : 2093-01-13, David Hale, M.D.',
   'IP: 203.120.223.13.',
   'The driver's license no:A334455B.',
   'the SSN:324598674 and e-mail: hale@gmail.com.',
   'Name : Hendrickson, Ora MR. # 719435 Date : 01/13/93.',
   'PCP : Oliveira, 25 years-old.',
   'Record date : 2079-11-09, Patient's VIN : 1HGBH41JXMN109286.'],
'masked': ['Record date : <DATE>, <DOCTOR>, M.D.',
   'IP: <IPADDR>.',
   'The driver's license <DLN>.',
   'the <SSN> and e-mail: <EMAIL>.',
   'Name : <PATIENT> MR. # <MEDICALRECORD> Date : <DATE>.',
   'PCP : <DOCTOR>, <AGE> years-old.',
   'Record date : <DATE>, Patient's VIN : <VIN>.'],
'obfuscated': ['Record date : 2093-01-18, Dr Alveria Eden, M.D.',
   'IP: 001.001.001.001.',
   'The driver's license K783518004444.',
   'the SSN-400-50-8849 and e-mail: Merilynn@hotmail.com.',
   'Name : Charls Danger MR. # J3366417 Date : 01-18-1974.',
   'PCP : Dr Sina Sewer, 55 years-old.',
   'Record date : 2079-11-23, Patient's VIN : 6ffff55gggg666777.'],
'ner_chunk': ['2093-01-13',
   'David Hale',
   'no:A334455B',
   'SSN:324598674',
   'Hendrickson, Ora',
   '719435',
   '01/13/93',
   'Oliveira',
   '25',
   '2079-11-09',
   '1HGBH41JXMN109286']}
```

#### Chunk filtering based on confidence

We added a new annotator ChunkFiltererApproach that allows to load a csv with both entities and confidence thresholds. 
This annotator will produce a ChunkFilterer model.

You can load the dictionary with the following property `setEntitiesConfidenceResource()`.

An example dictionary is:

```CSV
TREATMENT,0.7
```

With that dictionary, the user can filter the chunks corresponding to treatment entities which have confidence lower than 0.7.

Example:

We have a ner_chunk column and sentence column with the following data:

Ner_chunk
```
|[{chunk, 141, 163, the genomicorganization, {entity -> TREATMENT, sentence -> 0, chunk -> 0, confidence -> 0.57785}, []}, {chunk, 209, 267, a candidate gene forType II 
           diabetes mellitus, {entity -> PROBLEM, sentence -> 0, chunk -> 1, confidence -> 0.6614286}, []}, {chunk, 394, 408, byapproximately, {entity -> TREATMENT, sentence -> 1, chunk -> 2, confidence -> 0.7705}, []}, {chunk, 478, 508, single nucleotide polymorphisms, {entity -> TREATMENT, sentence -> 2, chunk -> 3, confidence -> 0.7204666}, []}, {chunk, 559, 581, aVal366Ala substitution, {entity -> TREATMENT, sentence -> 2, chunk -> 4, confidence -> 0.61505}, []}, {chunk, 588, 601, an 8 base-pair, {entity -> TREATMENT, sentence -> 2, chunk -> 5, confidence -> 0.29226667}, []}, {chunk, 608, 625, insertion/deletion, {entity -> PROBLEM, sentence -> 3, chunk -> 6, confidence -> 0.9841}, []}]|
+-------
```
Sentence
```
[{document, 0, 298, The human KCNJ9 (Kir 3.3, GIRK3) is a member of the G-protein-activated inwardly rectifying potassium (GIRK) channel family.Here we describe the genomicorganization of the KCNJ9 locus on chromosome 1q21-23 as a candidate gene forType II 
             diabetes mellitus in the Pima Indian population., {sentence -> 0}, []}, {document, 300, 460, The gene spansapproximately 7.6 kb and contains one noncoding and two coding exons ,separated byapproximately 2.2 and approximately 2.6 kb introns, respectively., {sentence -> 1}, []}, {document, 462, 601, We identified14 single nucleotide polymorphisms (SNPs),
             including one that predicts aVal366Ala substitution, and an 8 base-pair, {sentence -> 2}, []}, {document, 603, 626, (bp) insertion/deletion., {sentence -> 3}, []}]
```

We can filter the entities using the following annotator:

```python
        chunker_filter = ChunkFiltererApproach().setInputCols("sentence", "ner_chunk") \
            .setOutputCol("filtered") \
            .setCriteria("regex") \
            .setRegex([".*"]) \         
            .setEntitiesConfidenceResource("entities_confidence.csv")

```
Where entities-confidence.csv has the following data:

```csv
TREATMENT,0.7
PROBLEM,0.9
```
We can use that chunk_filter:

```
chunker_filter.fit(data).transform(data)
```
Producing the following entities:

```
|[{chunk, 394, 408, byapproximately, {entity -> TREATMENT, sentence -> 1, chunk -> 2, confidence -> 0.7705}, []}, {chunk, 478, 508, single nucleotide polymorphisms, {entity -> TREATMENT, sentence -> 2, chunk -> 3, confidence -> 0.7204666}, []}, {chunk, 608, 625, insertion/deletion, {entity -> PROBLEM, sentence -> 3, chunk -> 6, confidence -> 0.9841}, []}]|

```
As you can see, only the treatment entities with confidence score of more than 0.7, and the problem entities with confidence score of more than 0.9 have been kept in the output.


#### Extended regex dictionary fuctionallity in Deidentification

The RegexPatternsDictionary can now use a regex that spawns the 2 previous token and the 2 next tokens.
That feature is implemented using regex groups.

Examples: 

Given the sentence `The patient with ssn 123123123` we can use the following regex to capture the entitty `ssn (\d{9})`
Given the sentence `The patient has 12 years` we can use the following regex to capture the entitty `(\d{2}) years`

#### Enhanced RelationExtractionDL Model to create and identify relations between entities across the entire document

A new option has been added to `RENerChunksFilter` to support pairing entities from different sentences using `.setDocLevelRelations(True)`, to pass to the Relation Extraction Model. The RelationExtractionDL Model has also been updated to process document-level relations.

How to use:

```python
        re_dl_chunks = RENerChunksFilter() \
            .setInputCols(["ner_chunks", "dependencies"])\
            .setDocLevelRelations(True)\
            .setMaxSyntacticDistance(7)\
            .setOutputCol("redl_ner_chunks")  
```

Examples:

Given a document containing multiple sentences: `John somkes cigrettes. He also consumes alcohol.`, now we can generate relation pairs across sentences and relate `alcohol` with `John` .

#### Set NER graph explicitely in MedicalNerApproach
Now MedicalNerApproach can receives the path to the graph directly. When a graph location is provided through this method, previous graph search behavior is disabled.
```
MedicalNerApproach.setGraphFile(graphFilePath)
```

#### MedicalNerApproach can now accept a user-defined name for log file.
Now MedicalNerApproach can accept a user-defined name for the log file. If not such a name is provided, the conventional naming will take place.
```
MedicalNerApproach.setLogPrefix("oncology_ner")
```
This will result in `oncology_ner_20210605_141701.log` filename being used, in which the `20210605_141701` is a timestamp.

#### New Notebooks

+ A [new notebook](https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/1.4.Biomedical_NER_SparkNLP_paper_reproduce.ipynb)  to reproduce our peer-reviewed NER paper (https://arxiv.org/abs/2011.06315)
+ New databricks [case study notebooks](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/databricks/python/healthcare_case_studies). In these notebooks, we showed the examples of how to work with oncology notes dataset and OCR on databricks for both DBr and community edition versions.


### 3.0.3

We are glad to announce that Spark NLP for Healthcare 3.0.3 has been released!

#### Highlights

+ Five new entity resolution models to cover UMLS, HPO and LIONC terminologies.
+ New feature for random displacement of dates on deidentification model.
+ Five new pretrained pipelines to map terminologies across each other (from UMLS to ICD10, from RxNorm to MeSH etc.)
+ AnnotationToolReader support for Spark 2.3. The tool that helps model training on Spark-NLP to leverage data annotated using JSL Annotation Tool now has support for Spark 2.3.
+ Updated documentation (Scaladocs) covering more APIs, and examples. 

#### Five new resolver models:

+ `sbiobertresolve_umls_major_concepts`: This model returns CUI (concept unique identifier) codes for Clinical Findings, Medical Devices, Anatomical Structures and Injuries & Poisoning terms.            
+ `sbiobertresolve_umls_findings`: This model returns CUI (concept unique identifier) codes for 200K concepts from clinical findings.
+ `sbiobertresolve_loinc`: Map clinical NER entities to LOINC codes using `sbiobert`.
+ `sbluebertresolve_loinc`: Map clinical NER entities to LOINC codes using `sbluebert`.
+ `sbiobertresolve_HPO`: This model returns Human Phenotype Ontology (HPO) codes for phenotypic abnormalities encountered in human diseases. It also returns associated codes from the following vocabularies for each HPO code:

		* MeSH (Medical Subject Headings)
		* SNOMED
		* UMLS (Unified Medical Language System )
		* ORPHA (international reference resource for information on rare diseases and orphan drugs)
		* OMIM (Online Mendelian Inheritance in Man)

  *Related Notebook*: [Resolver Models](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/24.Improved_Entity_Resolvers_in_SparkNLP_with_sBert.ipynb)
  
#### New feature on Deidentification Module
+ isRandomDateDisplacement(True): Be able to apply a random displacement on obfuscation dates. The randomness is based on the seed.
+ Fix random dates when the format is not correct. Now you can repeat an execution using a seed for dates. Random dates will be based on the seed. 

#### Five new healthcare code mapping pipelines:

+ `icd10cm_umls_mapping`: This pretrained pipeline maps ICD10CM codes to UMLS codes without using any text data. You’ll just feed white space-delimited ICD10CM codes and it will return the corresponding UMLS codes as a list. If there is no mapping, the original code is returned with no mapping.

      {'icd10cm': ['M89.50', 'R82.2', 'R09.01'], 
          'umls': ['C4721411', 'C0159076', 'C0004044']}

+ `mesh_umls_mapping`: This pretrained pipeline maps MeSH codes to UMLS codes without using any text data. You’ll just feed white space-delimited MeSH codes and it will return the corresponding UMLS codes as a list. If there is no mapping, the original code is returned with no mapping.

      {'mesh': ['C028491', 'D019326', 'C579867'],
         'umls': ['C0970275', 'C0886627', 'C3696376']}

+ `rxnorm_umls_mapping`: This pretrained pipeline maps RxNorm codes to UMLS codes without using any text data. You’ll just feed white space-delimited RxNorm codes and it will return the corresponding UMLS codes as a list. If there is no mapping, the original code is returned with no mapping.

      {'rxnorm': ['1161611', '315677', '343663'],
         'umls': ['C3215948', 'C0984912', 'C1146501']}

+ `rxnorm_mesh_mapping`: This pretrained pipeline maps RxNorm codes to MeSH codes without using any text data. You’ll just feed white space-delimited RxNorm codes and it will return the corresponding MeSH codes as a list. If there is no mapping, the original code is returned with no mapping.

      {'rxnorm': ['1191', '6809', '47613'],
         'mesh': ['D001241', 'D008687', 'D019355']}

+ `snomed_umls_mapping`: This pretrained pipeline maps SNOMED codes to UMLS codes without using any text data. You’ll just feed white space-delimited SNOMED codes and it will return the corresponding UMLS codes as a list. If there is no mapping, the original code is returned with no mapping.

      {'snomed': ['733187009', '449433008', '51264003'],
         'umls': ['C4546029', 'C3164619', 'C0271267']}

  *Related Notebook*: [Healthcare Code Mapping](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/11.1.Healthcare_Code_Mapping.ipynb)


### 3.0.2

We are very excited to announce that **Spark NLP for Healthcare 3.0.2** has been released! This release includes bug fixes and some compatibility improvements.

#### Highlights

* Dictionaries for Obfuscator were augmented with more than 10K names.
* Improved support for spark 2.3 and spark 2.4.
* Bug fixes in `DrugNormalizer`.

#### New Features
Provide confidence scores for all available tags in `MedicalNerModel`,

##### MedicalNerModel before 3.0.2
```
[[named_entity, 0, 9, B-PROBLEM, [word -> Pneumonia, confidence -> 0.9998], []]
```
##### Now in Spark NLP for Healthcare 3.0.2
```
[[named_entity, 0, 9, B-PROBLEM, [B-PROBLEM -> 0.9998, I-TREATMENT -> 0.0, I-PROBLEM -> 0.0, I-TEST -> 0.0, B-TREATMENT -> 1.0E-4, word -> Pneumonia, B-TEST -> 0.0], []]
```

### 3.0.1

We are very excited to announce that **Spark NLP for Healthcare 3.0.1** has been released! 

#### Highlights:

* Fixed problem in Assertion Status internal tokenization (reported in Spark-NLP #2470).
* Fixes in the internal implementation of DeIdentificationModel/Obfuscator.
* Being able to disable the use of regexes in the Deidentification process 
* Other minor bug fixes & general improvements.

#### DeIdentificationModel Annotator

##### New `seed` parameter.
Now we have the possibility of using a seed to guide the process of obfuscating entities and returning the same result across different executions. To make that possible a new method setSeed(seed:Int) was introduced.

**Example:**
Return obfuscated documents in a repeatable manner based on the same seed.
##### Scala
```scala
deIdentification = DeIdentification()
      .setInputCols(Array("ner_chunk", "token", "sentence"))
      .setOutputCol("dei")
      .setMode("obfuscate")
      .setObfuscateRefSource("faker")
      .setSeed(10)
      .setIgnoreRegex(true)
```
##### Python
```python
de_identification = DeIdentification() \
            .setInputCols(["ner_chunk", "token", "sentence"]) \
            .setOutputCol("dei") \
            .setMode("obfuscate") \
            .setObfuscateRefSource("faker") \
            .setSeed(10) \
            .setIgnoreRegex(True)

```

This seed controls how the obfuscated values are picked from a set of obfuscation candidates. Fixing the seed allows the process to be replicated.

**Example:**

Given the following input to the deidentification:
```
"David Hale was in Cocke County Baptist Hospital. David Hale"
```

If the annotator is set up with a seed of 10:
##### Scala
```
val deIdentification = new DeIdentification()
      .setInputCols(Array("ner_chunk", "token", "sentence"))
      .setOutputCol("dei")
      .setMode("obfuscate")
      .setObfuscateRefSource("faker")
      .setSeed(10)
      .setIgnoreRegex(true)
```
##### Python
```python
de_identification = DeIdentification() \
            .setInputCols(["ner_chunk", "token", "sentence"]) \
            .setOutputCol("dei") \
            .setMode("obfuscate") \
            .setObfuscateRefSource("faker") \
            .setSeed(10) \
            .setIgnoreRegex(True)

```

The result will be the following for any execution,

```
"Brendan Kitten was in New Megan.Brendan Kitten"
```
Now if we set up a seed of 32,
##### Scala

```scala
val deIdentification = new DeIdentification()
      .setInputCols(Array("ner_chunk", "token", "sentence"))
      .setOutputCol("dei")
      .setMode("obfuscate")
      .setObfuscateRefSource("faker")
      .setSeed(32)
      .setIgnoreRegex(true)
```
##### Python
```python
de_identification = DeIdentification() \
            .setInputCols(["ner_chunk", "token", "sentence"]) \
            .setOutputCol("dei") \
            .setMode("obfuscate") \
            .setObfuscateRefSource("faker") \
            .setSeed(10) \
            .setIgnoreRegex(True)
```

The result will be the following for any execution,

```
"Louise Pear was in Lake Edward.Louise Pear"
```

##### New `ignoreRegex` parameter.
You can now choose to completely disable the use of regexes in the deidentification process by setting the setIgnoreRegex param to True.
**Example:**
##### Scala

```scala
DeIdentificationModel.setIgnoreRegex(true)
```
##### Python
```python
DeIdentificationModel().setIgnoreRegex(True)
```

The default value for this param is `False` meaning that regexes will be used by default.

##### New supported entities for Deidentification & Obfuscation:

We added new entities to the default supported regexes:

* `SSN - Social security number.`
* `PASSPORT - Passport id.`
* `DLN - Department of Labor Number.`
* `NPI - National Provider Identifier.`
* `C_CARD - The id number for credits card.`
* `IBAN - International Bank Account Number.`
* `DEA - DEA Registration Number, which is an identifier assigned to a health care provider by the United States Drug Enforcement Administration.`

We also introduced new Obfuscator cases for these new entities.


### 3.0.0

We are very excited to announce that **Spark NLP for Healthcare 3.0.0** has been released! This has been one of the biggest releases we have ever done and we are so proud to share this with our customers.

#### Highlights:

Spark NLP for Healthcare 3.0.0 extends the support for Apache Spark 3.0.x and 3.1.x major releases on Scala 2.12 with both Hadoop 2.7. and 3.2. We now support all 4 major Apache Spark and PySpark releases of 2.3.x, 2.4.x, 3.0.x, and 3.1.x helping the customers to migrate from earlier Apache Spark versions to newer releases without being worried about Spark NLP support.

#### Highlights:
* Support for Apache Spark and PySpark 3.0.x on Scala 2.12
* Support for Apache Spark and PySpark 3.1.x on Scala 2.12
* Migrate to TensorFlow v2.3.1 with native support for Java to take advantage of many optimizations for CPU/GPU and new features/models introduced in TF v2.x
* A brand new `MedicalNerModel` annotator to train & load the licensed clinical NER models.
*  **Two times faster NER and Entity Resolution** due to new batch annotation technique.
* Welcoming 9x new Databricks runtimes to our Spark NLP family:
  * Databricks 7.3
  * Databricks 7.3 ML GPU
  * Databricks 7.4
  * Databricks 7.4 ML GPU
  * Databricks 7.5
  * Databricks 7.5 ML GPU
  * Databricks 7.6
  * Databricks 7.6 ML GPU
  * Databricks 8.0
  * Databricks 8.0 ML (there is no GPU in 8.0)
  * Databricks 8.1 Beta
* Welcoming 2x new EMR 6.x series to our Spark NLP family:
  * EMR 6.1.0 (Apache Spark 3.0.0 / Hadoop 3.2.1)
  * EMR 6.2.0 (Apache Spark 3.0.1 / Hadoop 3.2.1)
* Starting Spark NLP for Healthcare 3.0.0 the default packages  for CPU and GPU will be based on Apache Spark 3.x and Scala 2.12.

##### Deprecated

Text2SQL annotator is deprecated and will not be maintained going forward. We are working on a better and faster version of Text2SQL at the moment and will announce soon.

#### 1. MedicalNerModel Annotator

Starting Spark NLP for Healthcare 3.0.0, the licensed clinical and biomedical pretrained NER models will only work with this brand new annotator called `MedicalNerModel` and will not work with `NerDLModel` in open source version.

In order to make this happen, we retrained all the clinical NER models (more than 80) and uploaded to models hub.

Example:


    clinical_ner = MedicalNerModel.pretrained("ner_clinical", "en", "clinical/models") \
    .setInputCols(["sentence", "token", "embeddings"])\
    .setOutputCol("ner")

#### 2. Speed Improvements

A new batch annotation technique implemented in Spark NLP 3.0.0 for `NerDLModel`,`BertEmbeddings`, and `BertSentenceEmbeddings` annotators will be reflected in `MedicalNerModel` and it improves prediction/inferencing performance radically. From now on the `batchSize` for these annotators means the number of rows that can be fed into the models for prediction instead of sentences per row. You can control the throughput when you are on accelerated hardware such as GPU to fully utilise it. Here are the overall speed comparison:

Now, NER inference and Entity Resolution are **two times faster** on CPU and three times faster on GPU.


#### 3. JSL Clinical NER Model

We are releasing the richest clinical NER model ever, spanning over 80 entities. It has been under development for the last 6 months and we manually annotated more than 4000 clinical notes to cover such a high number of entities in a single model. It has 4 variants at the moment:

- `jsl_ner_wip_clinical`
- `jsl_ner_wip_greedy_clinical`
- `jsl_ner_wip_modifier_clinical`
- `jsl_rd_ner_wip_greedy_clinical`

##### Entities:

`Kidney_Disease`, `HDL`, `Diet`, `Test`, `Imaging_Technique`, `Triglycerides`, `Obesity`, `Duration`, `Weight`, `Social_History_Header`, `ImagingTest`, `Labour_Delivery`, `Disease_Syndrome_Disorder`, `Communicable_Disease`, `Overweight`, `Units`, `Smoking`, `Score`, `Substance_Quantity`, `Form`, `Race_Ethnicity`, `Modifier`, `Hyperlipidemia`, `ImagingFindings`, `Psychological_Condition`, `OtherFindings`, `Cerebrovascular_Disease`, `Date`, `Test_Result`, `VS_Finding`, `Employment`, `Death_Entity`, `Gender`, `Oncological`, `Heart_Disease`, `Medical_Device`, `Total_Cholesterol`, `ManualFix`, `Time`, `Route`, `Pulse`, `Admission_Discharge`, `RelativeDate`, `O2_Saturation`, `Frequency`, `RelativeTime`, `Hypertension`, `Alcohol`, `Allergen`, `Fetus_NewBorn`, `Birth_Entity`, `Age`, `Respiration`, `Medical_History_Header`, `Oxygen_Therapy`, `Section_Header`, `LDL`, `Treatment`, `Vital_Signs_Header`, `Direction`, `BMI`, `Pregnancy`, `Sexually_Active_or_Sexual_Orientation`, `Symptom`, `Clinical_Dept`, `Measurements`, `Height`, `Family_History_Header`, `Substance`, `Strength`, `Injury_or_Poisoning`, `Relationship_Status`, `Blood_Pressure`, `Drug`, `Temperature`, `EKG_Findings`, `Diabetes`, `BodyPart`, `Vaccine`, `Procedure`, `Dosage`


#### 4. JSL Clinical Assertion Model

We are releasing a brand new clinical assertion model, supporting 8 assertion statuses.

- `jsl_assertion_wip`


##### Assertion Labels :

`Present`, `Absent`, `Possible`, `Planned`, `Someoneelse`, `Past`, `Family`, `Hypotetical`

#### 5. Library Version Compatibility Table :

Spark NLP for Healthcare 3.0.0 is compatible with Spark NLP 3.0.1

#### 6. Pretrained Models Version Control (Beta):

Due to active release cycle, we are adding & training new pretrained models at each release and it might be tricky to maintain the backward compatibility or keep up with the latest models, especially for the users using our models locally in air-gapped networks.

We are releasing a new utility class to help you check your local & existing models with the latest version of everything we have up to date. You will not need to specify your AWS credentials from now on. This is the second version of the model checker we released with 2.7.6 and will replace that soon.

    from sparknlp_jsl.compatibility_beta import CompatibilityBeta

    compatibility = CompatibilityBeta(spark)

    print(compatibility.findVersion("ner_deid"))


#### 7. Updated Pretrained Models:

 (requires fresh `.pretraned()`)

None


### 2.7.6

We are glad to announce that Spark NLP for Healthcare 2.7.6 has been released!

#### Highlights:

- New pretrained **Radiology Assertion Status** model to assign `Confirmed`, `Suspected`, `Negative` assertion scopes to imaging findings or any clinical tests.

- **Obfuscating** the same sensitive information (patient or doctor name) with the same fake names across the same clinical note.

- Version compatibility checker for the pretrained clinical models and builds to keep up with the latest development efforts in production.

- Adding more English names to faker module in **Deidentification**.

- Updated & improved clinical **SentenceDetectorDL** model.

- New upgrades on `ner_deid_large` and `ner_deid_enriched` NER models to cover more use cases with better resolutions.

- Adding more [examples](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/scala/healthcare) to workshop repo for _Scala_ users to practice more on healthcare annotators. 

- Bug fixes & general improvements.

#### 1. Radiology Assertion Status Model

We trained a new assertion model to assign `Confirmed`, `Suspected`, `Negative` assertion scopes to imaging findings or any clinical tests. It will try to assign these statuses to any named entity you would feed to the assertion annotater in the same pipeline.

     radiology_assertion = AssertionDLModel.pretrained("assertion_dl_radiology", "en", "clinical/models")\
     .setInputCols(["sentence", "ner_chunk", "embeddings"])\
     .setOutputCol("assertion")

`text = Blunting of the left costophrenic angle on the lateral view posteriorly suggests a small left pleural effusion. No right-sided pleural effusion or pneumothorax is definitively seen. There are mildly displaced fractures of the left lateral 8th and likely 9th ribs.`


|sentences |chunk | ner_label |sent_id|assertion|
|-----------:|:-----:|:---------:|:------:|:------|
|Blunting of the left costophrenic angle on the lateral view posteriorly suggests a small left pleural effusion.|Blunting           |ImagingFindings|0      |Confirmed|
|Blunting of the left costophrenic angle on the lateral view posteriorly suggests a small left pleural effusion.|effusion           |ImagingFindings|0      |Suspected|
|No right-sided pleural effusion or pneumothorax is definitively seen.                                          |effusion           |ImagingFindings|1      |Negative |
|No right-sided pleural effusion or pneumothorax is definitively seen.                                          |pneumothorax       |ImagingFindings|1      |Negative |
|There are mildly displaced fractures of the left lateral 8th and likely 9th ribs.                              |displaced fractures|ImagingFindings|2      |Confirmed|

You can also use this with `AssertionFilterer` to return clinical findings from a note only when it is i.e. `confirmed` or `suspected`.

     assertion_filterer = AssertionFilterer()\
     .setInputCols("sentence","ner_chunk","assertion")\
     .setOutputCol("assertion_filtered")\
     .setWhiteList(["confirmed","suspected"])

     >> ["displaced fractures", "effusion"]

#### 2. **Obfuscating** with the same fake name across the same note:

     obfuscation = DeIdentification()\
      .setInputCols(["sentence", "token", "ner_chunk"]) \
      .setOutputCol("deidentified") \
      .setMode("obfuscate")\
      .setObfuscateDate(True)\
      .setSameEntityThreshold(0.8)\
      .setObfuscateRefSource("faker")

      
    text =''' Provider: David Hale, M.D.
              Pt: Jessica Parker 
              David told  Jessica that she will need to visit the clinic next month.'''



|    | sentence                                                               | obfuscated                                                          |
|---:|:-----------------------------------------------------------------------|:----------------------------------------------------------------------|
|  0 | Provider: `David Hale`, M.D.                                             | Provider: `Dennis Perez`, M.D.                                          |
|  1 | Pt: `Jessica Parker`                                                     | Pt: `Gerth Bayer`                                                       |
|  2 | `David` told  `Jessica` that she will need to visit the clinic next month. | `Dennis` told  `Gerth` that she will need to visit the clinic next month. |

#### 3. Library Version Compatibility Table :

We are releasing the version compatibility table to help users get to see which Spark NLP licensed version is built against which core (open source) version. We are going to release a detailed one after running some tests across the jars from each library.

| Healthcare| Public |
|-----------|--------|
| 2.7.6     | 2.7.4  |
| 2.7.5     | 2.7.4  |
| 2.7.4     | 2.7.3  |
| 2.7.3     | 2.7.3  |
| 2.7.2     | 2.6.5  |
| 2.7.1     | 2.6.4  |
| 2.7.0     | 2.6.3  |
| 2.6.2     | 2.6.2  |
| 2.6.0     | 2.6.0  |
| 2.5.5     | 2.5.5  |
| 2.5.3     | 2.5.3  |
| 2.5.2     | 2.5.2  |
| 2.5.0     | 2.5.0  |
| 2.4.7     | 2.4.5  |
| 2.4.6     | 2.4.5  |
| 2.4.5     | 2.4.5  |
| 2.4.2     | 2.4.2  |
| 2.4.1     | 2.4.1  |
| 2.4.0     | 2.4.0  |
| 2.3.6     | 2.3.6  |
| 2.3.5     | 2.3.5  |
| 2.3.4     | 2.3.4  |


#### 4. Pretrained Models Version Control :

Due to active release cycle, we are adding & training new pretrained models at each release and it might be tricky to maintain the backward compatibility or keep up with the latest models, especially for the users using our models locally in air-gapped networks. 

We are releasing a new utility class to help you check your local & existing models with the latest version of everything we have up to date. This is an highly experimental feature of which we plan to improve and add more capability later on.


    from sparknlp_jsl.check_compatibility import Compatibility

     checker = sparknlp_jsl.Compatibility()

     result = checker.find_version(aws_access_key_id=license_keys['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=license_keys['AWS_SECRET_ACCESS_KEY'],
                            metadata_path=None,
                            model = 'all' , # or a specific model name
                            target_version='all',
                            cache_pretrained_path='/home/ubuntu/cache_pretrained')

     >> result['outdated_models']
     
      [{'model_name': 'clinical_ner_assertion',
        'current_version': '2.4.0',
        'latest_version': '2.6.4'},
       {'model_name': 'jsl_rd_ner_wip_greedy_clinical',
        'current_version': '2.6.1',
        'latest_version': '2.6.2'},
       {'model_name': 'ner_anatomy',
        'current_version': '2.4.2',
        'latest_version': '2.6.4'},
       {'model_name': 'ner_aspect_based_sentiment',
        'current_version': '2.6.2',
        'latest_version': '2.7.2'},
       {'model_name': 'ner_bionlp',
        'current_version': '2.4.0',
        'latest_version': '2.7.0'},
       {'model_name': 'ner_cellular',
        'current_version': '2.4.2',
        'latest_version': '2.5.0'}]

      >> result['version_comparison_dict']
      
      [{'clinical_ner_assertion': {'current_version': '2.4.0', 'latest_version': '2.6.4'}}, {'jsl_ner_wip_clinical': {'current_version': '2.6.5', 'latest_version': '2.6.1'}}, {'jsl_ner_wip_greedy_clinical': {'current_version': '2.6.5', 'latest_version': '2.6.5'}}, {'jsl_ner_wip_modifier_clinical': {'current_version': '2.6.4', 'latest_version': '2.6.4'}}, {'jsl_rd_ner_wip_greedy_clinical': {'current_version': '2.6.1','latest_version': '2.6.2'}}]

#### 5. Updated Pretrained Models:

 (requires fresh `.pretraned()`)
 
- ner_deid_large
- ner_deid_enriched


### 2.7.5

We are glad to announce that Spark NLP for Healthcare 2.7.5 has been released!  

#### Highlights:

- New pretrained **Relation Extraction** model to link clinical tests to test results and dates to clinical entities: `re_test_result_date`
- Adding two new `Admission` and `Discharge` entities to `ner_events_clinical` and renaming it to `ner_events_admission_clinical`
- Improving `ner_deid_enriched` NER model to cover `Doctor` and `Patient` name entities in various context and notations.
- Bug fixes & general improvements.

#### 1. re_test_result_date :

text = "Hospitalized with pneumonia in June, confirmed by a positive PCR of any specimen, evidenced by SPO2 </= 93% or PaO2/FiO2 < 300 mmHg"

|    | Chunk-1   | Entity-1   | Chunk-2   | Entity-2    | Relation     |
|---:|:----------|:-----------|:----------|:------------|:-------------|
|  0 | pneumonia | Problem    | june      | Date        | is_date_of   |
|  1 | PCR       | Test       | positive  | Test_Result | is_result_of |
|  2 | SPO2      | Test       | 93%       | Test_Result | is_result_of |
|  3 | PaO2/FiO2 | Test       | 300 mmHg  | Test_Result | is_result_of |

#### 2. `ner_events_admission_clinical` :

`ner_events_clinical` NER model is updated & improved to include `Admission` and `Discharge` entities.

text ="She is diagnosed as cancer in 1991. Then she was admitted to Mayo Clinic in May 2000 and discharged in October 2001"

|    | chunk        | entity        |
|---:|:-------------|:--------------|
|  0 | diagnosed    | OCCURRENCE    |
|  1 | cancer       | PROBLEM       |
|  2 | 1991         | DATE          |
|  3 | admitted     | ADMISSION     |
|  4 | Mayo Clinic  | CLINICAL_DEPT |
|  5 | May 2000     | DATE          |
|  6 | discharged   | DISCHARGE     |
|  7 | October 2001 | DATE          |


#### 3. Improved `ner_deid_enriched` :

PHI NER model is retrained to cover `Doctor` and `Patient` name entities even there is a punctuation between tokens as well as all upper case or lowercased.

text ="A . Record date : 2093-01-13 , DAVID HALE , M.D . , Name : Hendrickson , Ora MR . # 7194334 Date : 01/13/93 PCP : Oliveira , 25 month years-old , Record date : 2079-11-09 . Cocke County Baptist Hospital . 0295 Keats Street"

|    | chunk                         | entity        |
|---:|:------------------------------|:--------------|
|  0 | 2093-01-13                    | MEDICALRECORD |
|  1 | DAVID HALE                    | DOCTOR        |
|  2 | Hendrickson , Ora             | PATIENT       |
|  3 | 7194334                       | MEDICALRECORD |
|  4 | 01/13/93                      | DATE          |
|  5 | Oliveira                      | DOCTOR        |
|  6 | 25                            | AGE           |
|  7 | 2079-11-09                    | MEDICALRECORD |
|  8 | Cocke County Baptist Hospital | HOSPITAL      |
|  9 | 0295 Keats Street             | STREET        |


### 2.7.4

We are glad to announce that Spark NLP for Healthcare 2.7.4 has been released!  

#### Highlights:

- Introducing a new annotator to extract chunks with NER tags using regex-like patterns: **NerChunker**.
- Introducing two new annotators to filter chunks: **ChunkFilterer** and **AssertionFilterer**.
- Ability to change the entity type in **NerConverterInternal** without using ChunkMerger (`setReplaceDict`).
- In **DeIdentification** model, ability to use `faker` and static look-up lists at the same time randomly in `Obfuscation` mode.
- New **De-Identification NER** model, augmented with synthetic datasets to detect uppercased name entities.
- Bug fixes & general improvements.

#### 1. NerChunker:

Similar to what we used to do in **POSChunker** with POS tags, now we can also extract phrases that fits into a known pattern using the NER tags. **NerChunker** would be quite handy to extract entity groups with neighboring tokens when there is no pretrained NER model to address certain issues. Lets say we want to extract clinical findings and body parts together as a single chunk even if there are some unwanted tokens between. 

**How to use:**

    ner_model = NerDLModel.pretrained("ner_radiology", "en", "clinical/models")\
        .setInputCols("sentence","token","embeddings")\
        .setOutputCol("ner")
                
    ner_chunker = NerChunker().\
        .setInputCols(["sentence","ner"])\
        .setOutputCol("ner_chunk")\
        .setRegexParsers(["<IMAGINGFINDINGS>*<BODYPART>"])

    text = 'She has cystic cyst on her kidney.'

    >> ner tags: [(cystic, B-IMAGINGFINDINGS), (cyst,I-IMAGINGFINDINGS), (kidney, B-BODYPART)
    >> ner_chunk: ['cystic cyst on her kidney']


#### 2. ChunkFilterer:

**ChunkFilterer** will allow you to filter out named entities by some conditions or predefined look-up lists, so that you can feed these entities to other annotators like Assertion Status or Entity Resolvers.  It can be used with two criteria: **isin** and **regex**.

**How to use:**

    ner_model = NerDLModel.pretrained("ner_clinical", "en", "clinical/models")\
          .setInputCols("sentence","token","embeddings")\
          .setOutputCol("ner")

    ner_converter = NerConverter() \
          .setInputCols(["sentence", "token", "ner"]) \
          .setOutputCol("ner_chunk")
          
    chunk_filterer = ChunkFilterer()\
          .setInputCols("sentence","ner_chunk")\
          .setOutputCol("chunk_filtered")\
          .setCriteria("isin") \ 
          .setWhiteList(['severe fever','sore throat'])

    text = 'Patient with severe fever, sore throat, stomach pain, and a headache.'

    >> ner_chunk: ['severe fever','sore throat','stomach pain','headache']
    >> chunk_filtered: ['severe fever','sore throat']


#### 3. AssertionFilterer:

**AssertionFilterer** will allow you to filter out the named entities by the list of acceptable assertion statuses. This annotator would be quite handy if you want to set a white list for the acceptable assertion statuses like `present` or `conditional`; and do not want `absent` conditions get out of your pipeline.

**How to use:**

    clinical_assertion = AssertionDLModel.pretrained("assertion_dl", "en", "clinical/models") \
      .setInputCols(["sentence", "ner_chunk", "embeddings"]) \
      .setOutputCol("assertion")
    
    assertion_filterer = AssertionFilterer()\
      .setInputCols("sentence","ner_chunk","assertion")\
      .setOutputCol("assertion_filtered")\
      .setWhiteList(["present"])


    text = 'Patient with severe fever and sore throat, but no stomach pain.'

    >> ner_chunk: ['severe fever','sore throat','stomach pain','headache']
    >> assertion_filtered: ['severe fever','sore throat']

 
### 2.7.3

We are glad to announce that Spark NLP for Healthcare 2.7.3 has been released!  

#### Highlights:

- Introducing a brand-new **RelationExtractionDL Annotator** – Achieving SOTA results in clinical relation extraction using **BioBert**.
- Massive Improvements & feature enhancements in **De-Identification** module:
    - Introduction of **faker** augmentation in Spark NLP for Healthcare to generate random data for obfuscation in de-identification module.
    - Brand-new annotator for **Structured De-Identification**.
- **Drug Normalizer:**  Normalize medication-related phrases (dosage, form and strength) and abbreviations in text and named entities extracted by NER models.
- **Confidence scores** in **assertion** output : just like NER output, assertion models now also support confidence scores for each prediction.
- **Cosine similarity** metrics in entity resolvers to get more informative and semantically correct results.
- **AuxLabel** in the metadata of entity resolvers to return additional mappings.
- New **Relation Extraction** models to extract relations between **body parts** and clinical entities.
- New **Entity Resolver** models to extract billable medical codes.
- New **Clinical Pretrained NER** models.
- Bug fixes & general improvements.
- Matching the version with Spark NLP open-source v2.7.3.


#### 1. Improvements in De-Identification Module:

Integration of `faker` library to automatically generate random data like names, dates, addresses etc so users dont have to specify dummy data (custom obfuscation files can still be used). It also improves the obfuscation results due to a bigger pool of random values.

**How to use:**

Set the flag `setObfuscateRefSource` to `faker`

    deidentification = DeIdentification()
        .setInputCols(["sentence", "token", "ner_chunk"])\
		.setOutputCol("deidentified")\
		.setMode("obfuscate") \
		.setObfuscateRefSource("faker")

For more details: Check out this [notebook ](https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/4.Clinical_DeIdentification.ipynb)

#### 2. Structured De-Identification Module:

Introduction of a new annotator to handle de-identification of structured data. it  allows users to define a mapping of columns and their obfuscation policy. Users can also provide dummy data and map them to columns they want to replace values in.

**How to use:**

	obfuscator = StructuredDeidentification \
		(spark,{"NAME":"PATIENT","AGE":"AGE"},
		obfuscateRefSource = "faker")

	obfuscator_df = obfuscator.obfuscateColumns(df)

	obfuscator_df.select("NAME","AGE").show(truncate=False)

**Example:**

Input Data:

Name  | Age
------------- | -------------
Cecilia Chapman|83
Iris Watson    |9  
Bryar Pitts    |98
Theodore Lowe  |16
Calista Wise   |76

Deidentified:

Name  | Age
------------- | -------------
Menne Erdôs|20
 Longin Robinson     |31  
 Flynn Fiedlerová   |50
 John Wakeland  |21
Vanessa Andersson   |12


For more details: Check out this [notebook](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/4.Clinical_DeIdentification.ipynb).

#### 3. Introducing SOTA relation extraction model using BioBert

A brand-new end-to-end trained BERT model, resulting in massive improvements. Another new annotator (`ReChunkFilter`) is also developed for this new model to allow syntactic features work well with BioBert to extract relations.

**How to use:**

    re_ner_chunk_filter = RENerChunksFilter()\
        .setInputCols(["ner_chunks", "dependencies"])\
        .setOutputCol("re_ner_chunks")\
        .setRelationPairs(pairs)\
        .setMaxSyntacticDistance(4)

    re_model = RelationExtractionDLModel()\
        .pretrained(“redl_temporal_events_biobert”, "en", "clinical/models")\
        .setPredictionThreshold(0.9)\
        .setInputCols(["re_ner_chunks", "sentences"])\
        .setOutputCol("relations")


##### Benchmarks:

**on benchmark datasets**

model                           | Spark NLP ML model | Spark NLP DL model | benchmark
---------------------------------|-----------|-----------|-----------
re_temporal_events_clinical     | 68.29     | 71.0      | 80.2 [1](https://arxiv.org/pdf/2012.08790.pdf)
re_clinical                     | 56.45     | **69.2**      | 68.2      [2](ncbi.nlm.nih.gov/pmc/articles/PMC7153059/)
re_human_pheotype_gene_clinical | -         | **87.9**      | 67.2 [3](https://arxiv.org/pdf/1903.10728.pdf)
re_drug_drug_interaction        | -         | 72.1      | 83.8 [4](https://www.aclweb.org/anthology/2020.knlp-1.4.pdf)
re_chemprot                     | 76.69     | **94.1**      | 83.64 [5](https://www.aclweb.org/anthology/D19-1371.pdf)

**on in-house annotations**

model                           | Spark NLP ML model | Spark NLP DL model
---------------------------------|-----------|-----------
re_bodypart_problem             | 84.58     | 85.7
re_bodypart_procedure           | 61.0      | 63.3
re_date_clinical                | 83.0      | 84.0  
re_bodypart_direction           | 93.5      | 92.5  


For more details: Check out the [notebook](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/10.1.Clinical_Relation_Extraction_BodyParts_Models.ipynb) or [modelshub](https://nlp.johnsnowlabs.com/models?tag=relation_extraction).



#### 4. Drug Normalizer:

Standardize units of drugs and handle abbreviations in raw text or drug chunks identified by any NER model. This normalization significantly improves performance of entity resolvers.  

**How to use:**

    drug_normalizer = DrugNormalizer()\
        .setInputCols("document")\
        .setOutputCol("document_normalized")\
        .setPolicy("all") #all/abbreviations/dosages

**Examples:**

`drug_normalizer.transform("adalimumab 54.5 + 43.2 gm”)`

    >>> "adalimumab 97700 mg"

**Changes:** _combine_ `54.5` + `43.2` and _normalize_ `gm` to `mg`

`drug_normalizer.transform("Agnogenic one half cup”)`

    >>> "Agnogenic 0.5 oral solution"

**Changes:** _replace_ `one half` to the `0.5`, _normalize_ `cup` to the `oral solution`

`drug_normalizer.transform("interferon alfa-2b 10 million unit ( 1 ml ) injec”)`

    >>> "interferon alfa - 2b 10000000 unt ( 1 ml ) injection "

**Changes:** _convert_ `10 million unit` to the `10000000 unt`, _replace_ `injec` with `injection`

For more details: Check out this [notebook](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/23.Drug_Normalizer.ipynb)

#### 5. Assertion models to support confidence in output:

Just like NER output, assertion models now also provides _confidence scores_ for each prediction.

chunks  | entities | assertion | confidence
-----------|-----------|------------|-------------
a headache | PROBLEM | present |0.9992
anxious | PROBLEM | conditional |0.9039
alopecia | PROBLEM | absent |0.9992
pain | PROBLEM | absent |0.9238

`.setClasses()` method is deprecated in `AssertionDLApproach`  and users do not need to specify number of classes while training, as it will be inferred from the dataset.


#### 6. New Relation Extraction Models:


We are also releasing new relation extraction models to link the clinical entities to body parts and dates. These models are trained using binary relation extraction approach for better accuracy.

**- re_bodypart_direction :**  Relation Extraction between `Body Part` and `Direction` entities.

**Example:**

**Text:** _“MRI demonstrated infarction in the upper brain stem , left cerebellum and right basil ganglia”_

relations | entity1                     | chunk1     | entity2                     | chunk2        | confidence
-----------|-----------------------------|------------|-----------------------------|---------------|------------
1         | Direction                   | upper      | bodyPart | brain stem    | 0.999
0         | Direction                   | upper      | bodyPart | cerebellum    | 0.999
0         | Direction                   | upper      | bodyPart | basil ganglia | 0.999
0         | bodyPart | brain stem | Direction                   | left          | 0.999
0         | bodyPart | brain stem | Direction                   | right         | 0.999
1         | Direction                   | left       | bodyPart | cerebellum    | 1.0         
0         | Direction                   | left       | bodyPart | basil ganglia | 0.976
0         | bodyPart | cerebellum | Direction                   | right         | 0.953
1         | Direction                   | right      | bodyPart | basil ganglia | 1.0       


**- re_bodypart_problem :** Relation Extraction between `Body Part` and `Problem` entities.

**Example:**

**Text:** _“No neurologic deficits other than some numbness in his left hand.”_

relation | entity1   | chunk1              | entity2                      | chunk2   | confidence  
--|------------------|--------------------|-----------------------------|---------|-----------  
0 | Symptom   | neurologic deficits | bodyPart | hand     |          1
1 | Symptom   | numbness            | bodyPart | hand     |          1


**- re_bodypart_proceduretest :**  Relation Extraction between `Body Part` and `Procedure`, `Test` entities.

**Example:**

**Text:** _“TECHNIQUE IN DETAIL: After informed consent was obtained from the patient and his mother, the chest was scanned with portable ultrasound.”_

relation | entity1                      | chunk1   | entity2   | chunk2              | confidence  
---------|-----------------------------|---------|----------|--------------------|-----------
1 | bodyPart | chest    | Test      | portable ultrasound |    0.999

**-re_date_clinical :** Relation Extraction between `Date` and different clinical entities.   

**Example:**

**Text:** _“This 73 y/o patient had CT on 1/12/95, with progressive memory and cognitive decline since 8/11/94.”_

relations | entity1 | chunk1                                   | entity2 | chunk2  | confidence
-----------|---------|------------------------------------------|---------|---------|------------|
1         | Test    | CT                                       | Date    | 1/12/95 | 1.0
1         | Symptom | progressive memory and cognitive decline | Date    | 8/11/94 | 1.0


**How to use:**

    re_model = RelationExtractionModel()\
        .pretrained("re_bodypart_direction","en","clinical/models")\
        .setInputCols(["embeddings", "pos_tags", "ner_chunks", "dependencies"])\
        .setOutputCol("relations")\
        .setMaxSyntacticDistance(4)\
        .setRelationPairs([‘Internal_organ_or_component’, ‘Direction’])



For more details: Check out the [notebook](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/10.1.Clinical_Relation_Extraction_BodyParts_Models.ipynb) or [modelshub](https://nlp.johnsnowlabs.com/models?tag=relation_extraction).


**New matching scheme for entity resolvers - improved accuracy:** Adding the option to use `cosine similarity` to resolve entities and find closest matches, resulting in better, more semantically correct results.

#### 7. New Resolver Models using `JSL SBERT`:

+ `sbiobertresolve_icd10cm_augmented`

+ `sbiobertresolve_cpt_augmented`

+ `sbiobertresolve_cpt_procedures_augmented`

+ `sbiobertresolve_icd10cm_augmented_billable_hcc`

+ `sbiobertresolve_hcc_augmented`


**Returning auxilary columns mapped to resolutions:**  Chunk entity resolver and sentence entity resolver now returns auxilary data that is mapped the resolutions during training. This will allow users to get multiple resolutions with single model without using any other annotator in the pipeline (In order to get billable codes otherwise there needs to be other modules in the same pipeline)

**Example:**

`sbiobertresolve_icd10cm_augmented_billable_hcc`
**Input Text:** _"bladder cancer"_

idx | chunks | code | resolutions | all_codes | billable | hcc_status | hcc_score | all_distances   
---|---------------|-------|-------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|--------------------------|--------------------------|---------------------------|---------------------------------------------------
 0 | bladder cancer | C679 | ['bladder cancer', 'suspected bladder cancer', 'cancer in situ of urinary bladder', 'tumor of bladder neck', 'malignant tumour of bladder neck'] | ['C679', 'Z126', 'D090', 'D494', 'C7911'] | ['1', '1', '1', '1', '1'] | ['1', '0', '0', '0', '1'] | ['11', '0', '0', '0', '8'] | ['0.0000', '0.0904', '0.0978', '0.1080', '0.1281'] |

`sbiobertresolve_cpt_augmented`  
**Input Text:** _"ct abdomen without contrast"_

idx|  cpt code |   distance |resolutions                                                       
---:|------:|-----------:|:-------------------------------------------------------------------
0 | 74150 |     0.0802 | Computed tomography, abdomen; without contrast material            |
1 | 65091 |     0.1312 | Evisceration of ocular contents; without implant                   |
2 | 70450 |     0.1323 | Computed tomography, head or brain; without contrast material      |
3 | 74176 |     0.1333 | Computed tomography, abdomen and pelvis; without contrast material |
4 | 74185 |     0.1343 | Magnetic resonance imaging without contrast                        |
5 | 77059 |     0.1343 | Magnetic resonance imaging without contrast                        |

#### 8. New Pretrained Clinical NER Models

+ NER Radiology
**Input Text:** _"Bilateral breast ultrasound was subsequently performed, which demonstrated an ovoid mass measuring approximately 0.5 x 0.5 x 0.4 cm in diameter located within the anteromedial aspect of the left shoulder. This mass demonstrates isoechoic echotexture to the adjacent muscle, with no evidence of internal color flow. This may represent benign fibrous tissue or a lipoma."_

|idx | chunks                | entities                  |
|----|-----------------------|---------------------------|
| 0  | Bilateral             | Direction                 |
| 1  | breast                | BodyPart                  |
| 2  | ultrasound            | ImagingTest               |
| 3  | ovoid mass            | ImagingFindings           |
| 4  | 0.5 x 0.5 x 0.4       | Measurements              |
| 5  | cm                    | Units                     |
| 6  | anteromedial aspect   | Direction                 |
| 7  | left                  | Direction                 |
| 8  | shoulder              | BodyPart                  |
| 9  | mass                  | ImagingFindings           |
| 10 | isoechoic echotexture | ImagingFindings           |
| 11 | muscle                | BodyPart                  |
| 12 | internal color flow   | ImagingFindings           |
| 13 | benign fibrous tissue | ImagingFindings           |
| 14 | lipoma                | Disease_Syndrome_Disorder |



### 2.7.2

We are glad to announce that Spark NLP for Healthcare 2.7.2 has been released !

In this release, we introduce the following features:

+ Far better accuracy for resolving medication terms to RxNorm codes:

  `ondansetron 8 mg tablet' -> '312086`
+ Far better accuracy for resolving diagnosis terms to ICD-10-CM codes:

 `TIA -> transient ischemic attack (disorder)	‘S0690’`
+ New ability to map medications to pharmacological actions (PA):

  `'metformin' -> ‘Hypoglycemic Agents’ `
+ 2 new *greedy* named entity recognition models for medication details:

 `ner_drugs_greedy: ‘magnesium hydroxide 100mg/1ml PO’`

 ` ner_posology _greedy: ‘12 units of insulin lispro’ `

+ New model to *classify the gender* of a patient in a given medical note:

 `'58yo patient with a family history of breast cancer' -> ‘female’ `
+ And starting customized spark sessions with rich parameters

```python
        params = {"spark.driver.memory":"32G",
        "spark.kryoserializer.buffer.max":"2000M",
        "spark.driver.maxResultSize":"2000M"}

        spark = sparknlp_jsl.start(secret, params=params)
```
State-of-the-art accuracy is achieved using new healthcare-tuned BERT Sentence Embeddings (s-Bert). The following sections include more details, metrics, and examples.

#### Named Entity Recognizers for Medications


+ A new medication NER (`ner_drugs_greedy`) that joins the drug entities with neighboring entities such as  `dosage`, `route`, `form` and `strength`; and returns a single entity `drug`.  This greedy NER model would be highly useful if you want to extract a drug with its context and then use it to get a RxNorm code (drugs may get different RxNorm codes based on the dosage and strength information).

###### Metrics

| label  | tp    | fp   | fn   | prec  | rec   | f1    |
|--------|-------|------|------|-------|-------|-------|
| I-DRUG | 37423 | 4179 | 3773 | 0.899 | 0.908 | 0.904 |
| B-DRUG | 29699 | 2090 | 1983 | 0.934 | 0.937 | 0.936 |


+ A new medication NER (`ner_posology_greedy`) that joins the drug entities with neighboring entities such as  `dosage`, `route`, `form` and `strength`.  It also returns all the other medication entities even if not related to (or joined with) a drug.   

Now we have five different medication-related NER models. You can see the outputs from each model below:

Text = ''*The patient was prescribed 1 capsule of Advil 10 mg for 5 days and magnesium hydroxide 100mg/1ml suspension PO. He was seen by the endocrinology service and she was discharged on 40 units of insulin glargine at night, 12 units of insulin lispro with meals, and metformin 1000 mg two times a day.*''

a. **ner_drugs_greedy**

|   | chunks                           | begin | end | entities |
| - | -------------------------------- | ----- | --- | -------- |
| 0 | 1 capsule of Advil 10 mg         | 27    | 50  | DRUG     |
| 1 | magnesium hydroxide 100mg/1ml PO | 67    | 98  | DRUG     |
| 2 |  40 units of insulin glargine    | 168   | 195 | DRUG     |
| 3 |  12 units of insulin lispro      | 207   | 232 | DRUG     |

b. **ner_posology_greedy**

|    | chunks                           |   begin |   end | entities   |
|---:|:---------------------------------|--------:|------:|:-----------|
|  0 | 1 capsule of Advil 10 mg         |      27 |    50 | DRUG       |
|  1 | magnesium hydroxide 100mg/1ml PO |      67 |    98 | DRUG       |
|  2 | for 5 days                       |      52 |    61 | DURATION   |
|  3 | 40 units of insulin glargine     |     168 |   195 | DRUG       |
|  4 | at night                         |     197 |   204 | FREQUENCY  |
|  5 | 12 units of insulin lispro       |     207 |   232 | DRUG       |
|  6 | with meals                       |     234 |   243 | FREQUENCY  |
|  7 | metformin 1000 mg                |     250 |   266 | DRUG       |
|  8 | two times a day                  |     268 |   282 | FREQUENCY  |

c. **ner_drugs**

|    | chunks              |   begin |   end | entities   |
|---:|:--------------------|--------:|------:|:-----------|
|  0 | Advil               |      40 |    44 | DrugChem   |
|  1 | magnesium hydroxide |      67 |    85 | DrugChem   |
|  2 | metformin           |     261 |   269 | DrugChem   |


d.**ner_posology**

|    | chunks              |   begin |   end | entities   |
|---:|:--------------------|--------:|------:|:-----------|
|  0 | 1                   |      27 |    27 | DOSAGE     |
|  1 | capsule             |      29 |    35 | FORM       |
|  2 | Advil               |      40 |    44 | DRUG       |
|  3 | 10 mg               |      46 |    50 | STRENGTH   |
|  4 | for 5 days          |      52 |    61 | DURATION   |
|  5 | magnesium hydroxide |      67 |    85 | DRUG       |
|  6 | 100mg/1ml           |      87 |    95 | STRENGTH   |
|  7 | PO                  |      97 |    98 | ROUTE      |
|  8 | 40 units            |     168 |   175 | DOSAGE     |
|  9 | insulin glargine    |     180 |   195 | DRUG       |
| 10 | at night            |     197 |   204 | FREQUENCY  |
| 11 | 12 units            |     207 |   214 | DOSAGE     |
| 12 | insulin lispro      |     219 |   232 | DRUG       |
| 13 | with meals          |     234 |   243 | FREQUENCY  |
| 14 | metformin           |     250 |   258 | DRUG       |
| 15 | 1000 mg             |     260 |   266 | STRENGTH   |
| 16 | two times a day     |     268 |   282 | FREQUENCY  |

e. **ner_drugs_large**

|    | chunks                            |   begin |   end | entities   |
|---:|:----------------------------------|--------:|------:|:-----------|
|  0 | Advil 10 mg                       |      40 |    50 | DRUG       |
|  1 | magnesium hydroxide 100mg/1ml PO. |      67 |    99 | DRUG       |
|  2 | insulin glargine                  |     180 |   195 | DRUG       |
|  3 | insulin lispro                    |     219 |   232 | DRUG       |
|  4 | metformin 1000 mg                 |     250 |   266 | DRUG       |


#### Patient Gender Classification

This model detects the gender of the patient in the clinical document. It can classify the documents into `Female`, `Male` and `Unknown`.

We release two models:

+ 'Classifierdl_gender_sbert' (more accurate, works with licensed `sbiobert_base_cased_mli`)

+ 'Classifierdl_gender_biobert' (works with `biobert_pubmed_base_cased`)

The models are trained on more than four thousands clinical documents (radiology reports, pathology reports, clinical visits etc.), annotated internally.

###### Metrics `(Classifierdl_gender_sbert)`

|        | precision | recall | f1-score | support |
| ------ | --------- | ------ | -------- | ------- |
| Female | 0.9224    | 0.8954 | 0.9087   | 239     |
| Male   | 0.7895    | 0.8468 | 0.8171   | 124     |

Text= ''*social history: shows that  does not smoke cigarettes or drink alcohol, lives in a nursing home.
family history: shows a family history of breast cancer.*''

```python
gender_classifier.annotate(text)['class'][0]
>> `Female`
```

See this [Colab](https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/21_Gender_Classifier.ipynb) notebook for further details.

a. **classifierdl_gender_sbert**

```python

document = DocumentAssembler()\
    .setInputCol("text")\
    .setOutputCol("document")

sbert_embedder = BertSentenceEmbeddings\
    .pretrained("sbiobert_base_cased_mli", 'en', 'clinical/models')\
    .setInputCols(["document"])\
    .setOutputCol("sentence_embeddings")\
    .setMaxSentenceLength(512)

gender_classifier = ClassifierDLModel\
    .pretrained('classifierdl_gender_sbert', 'en', 'clinical/models') \
    .setInputCols(["document", "sentence_embeddings"]) \
    .setOutputCol("class")

gender_pred_pipeline = Pipeline(
    stages = [
       document,
       sbert_embedder,
       gender_classifier
            ])
```
b. **classifierdl_gender_biobert**

```python
documentAssembler = DocumentAssembler()\
    .setInputCol("text")\
    .setOutputCol("document")

clf_tokenizer = Tokenizer()\
    .setInputCols(["document"])\
    .setOutputCol("token")\

biobert_embeddings = BertEmbeddings().pretrained('biobert_pubmed_base_cased') \
    .setInputCols(["document",'token'])\
    .setOutputCol("bert_embeddings")

biobert_embeddings_avg = SentenceEmbeddings() \
    .setInputCols(["document", "bert_embeddings"]) \
    .setOutputCol("sentence_bert_embeddings") \
    .setPoolingStrategy("AVERAGE")

genderClassifier = ClassifierDLModel.pretrained('classifierdl_gender_biobert', 'en', 'clinical/models') \
    .setInputCols(["document", "sentence_bert_embeddings"]) \
    .setOutputCol("gender")

gender_pred_pipeline = Pipeline(
   stages = [
       documentAssembler,
       clf_tokenizer,
       biobert_embeddings,
       biobert_embeddings_avg,
       genderClassifier
   ])

   ```
#### New ICD10CM and RxCUI resolvers powered by s-Bert embeddings

The advent of s-Bert sentence embeddings changed the landscape of Clinical Entity Resolvers completely in Spark NLP. Since s-Bert is already tuned on [MedNLI](https://physionet.org/content/mednli/) (medical natural language inference) dataset, it is now capable of populating the chunk embeddings in a more precise way than before.

We now release two new resolvers:

+ `sbiobertresolve_icd10cm_augmented` (augmented with synonyms, four times richer than previous resolver accuracy:

    `73% for top-1 (exact match), 89% for top-5 (previous accuracy was 59% and 64% respectively)`

+ `sbiobertresolve_rxcui` (extract RxNorm concept unique identifiers to map with ATC or durg families)
accuracy:

    `71% for top-1 (exact match), 72% for top-5
(previous accuracy was 22% and 41% respectively)`

a. **ICD10CM augmented resolver**

Text = "*This is an 82 year old male with a history of prior tobacco use , hypertension , chronic renal insufficiency , COPD , gastritis , and TIA who initially presented to Braintree with a non-ST elevation MI and Guaiac positive stools , transferred to St . Margaret\'s Center for Women & Infants for cardiac catheterization with PTCA to mid LAD lesion complicated by hypotension and bradycardia requiring Atropine , IV fluids and transient dopamine possibly secondary to vagal reaction , subsequently transferred to CCU for close monitoring , hemodynamically stable at the time of admission to the CCU .* "

|    | chunk                       |   begin |   end | code   | term                                                     |
|---:|:----------------------------|--------:|------:|:-------|:---------------------------------------------------------|
|  0 | hypertension                |      66 |    77 | I10    | hypertension                                             |
|  1 | chronic renal insufficiency |      81 |   107 | N189   | chronic renal insufficiency                              |
|  2 | COPD                        |     111 |   114 | J449   | copd - chronic obstructive pulmonary disease             |
|  3 | gastritis                   |     118 |   126 | K2970  | gastritis                                                |
|  4 | TIA                         |     134 |   136 | S0690  | transient ischemic attack (disorder)		 |
|  5 | a non-ST elevation MI       |     180 |   200 | I219   | silent myocardial infarction (disorder)                  |
|  6 | Guaiac positive stools      |     206 |   227 | K921   | guaiac-positive stools                                   |
|  7 | mid LAD lesion              |     330 |   343 | I2102  | stemi involving left anterior descending coronary artery |
|  8 | hypotension                 |     360 |   370 | I959   | hypotension                                              |
|  9 | bradycardia                 |     376 |   386 | O9941  | bradycardia                                              |


b. **RxCUI resolver**

Text= "*He was seen by the endocrinology service and she was discharged on 50 mg of eltrombopag oral at night, 5 mg amlodipine with meals, and metformin 1000 mg two times a day .* "

|    | chunk                     |   begin |   end |   code | term                                        |
|---:|:--------------------------|--------:|------:|-------:|:--------------------------------------------|
|  0 | 50 mg of eltrombopag oral |      67 |    91 | 825427 | eltrombopag 50 MG Oral Tablet               |
|  1 | 5 mg amlodipine           |     103 |   117 | 197361 | amlodipine 5 MG Oral Tablet                 |
|  2 | metformin 1000 mg         |     135 |   151 | 861004 | metformin hydrochloride 1000 MG Oral Tablet |

Using this new resolver and some other resources like Snomed Resolver, RxTerm, MESHPA and ATC dictionary, you can link the drugs to the pharmacological actions (PA), ingredients and the disease treated with that.

###### Code sample:

(after getting the chunk from ChunkConverter)


 ```python

c2doc = Chunk2Doc().setInputCols("ner_chunk").setOutputCol("ner_chunk_doc")

sbert_embedder = BertSentenceEmbeddings\
    .pretrained("sbiobert_base_cased_mli",'en','clinical/models')\
    .setInputCols(["ner_chunk_doc"])\
    .setOutputCol("sbert_embeddings")

icd10_resolver = SentenceEntityResolverModel.pretrained("sbiobertresolve_icd10cm_augmented","en", "clinical/models") \
    .setInputCols(["ner_chunk", "sbert_embeddings"]) \
    .setOutputCol("icd10cm_code")\
    .setDistanceFunction("EUCLIDEAN")
```
See the [notebook](https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/3.Clinical_Entity_Resolvers.ipynb#scrollTo=VtDWAlnDList) for details.


### 2.7.1

We are glad to announce that Spark NLP for Healthcare 2.7.1 has been released !

In this release, we introduce the following features:

#### 1. Sentence BioBert and Bluebert Transformers that are fine tuned on [MedNLI](https://physionet.org/content/mednli/) dataset.

Sentence Transformers offers a framework that provides an easy method to compute dense vector representations for sentences and paragraphs (also known as sentence embeddings). The models are based on BioBert and BlueBert, and are tuned specifically to meaningful sentence embeddings such that sentences with similar meanings are close in vector space. These are the first PyTorch based models we managed to port into Spark NLP.

Here is how you can load these:
```python
sbiobert_embeddins = BertSentenceEmbeddings\
     .pretrained("sbiobert_base_cased_mli",'en','clinical/models')\
     .setInputCols(["ner_chunk_doc"])\
     .setOutputCol("sbert_embeddings")
```
```python
sbluebert_embeddins = BertSentenceEmbeddings\
     .pretrained("sbluebert_base_cased_mli",'en','clinical/models')\
     .setInputCols(["ner_chunk_doc"])\
     .setOutputCol("sbert_embeddings")
```

#### 2. SentenceEntityResolvers powered by s-Bert embeddings.

The advent of s-Bert sentence embeddings changed the landscape of Clinical Entity Resolvers completely in Spark NLP. Since s-Bert is already tuned on MedNLI (medical natural language inference) dataset, it is now capable of populating the chunk embeddings in a more precise way than before.

Using sbiobert_base_cased_mli, we trained the following Clinical Entity Resolvers:

sbiobertresolve_icd10cm  
sbiobertresolve_icd10pcs  
sbiobertresolve_snomed_findings (with clinical_findings concepts from CT version)  
sbiobertresolve_snomed_findings_int  (with clinical_findings concepts from INT version)  
sbiobertresolve_snomed_auxConcepts (with Morph Abnormality, Procedure, Substance, Physical Object, Body Structure concepts from CT version)  
sbiobertresolve_snomed_auxConcepts_int  (with Morph Abnormality, Procedure, Substance, Physical Object, Body Structure concepts from INT version)  
sbiobertresolve_rxnorm  
sbiobertresolve_icdo  
sbiobertresolve_cpt  

Code sample:

(after getting the chunk from ChunkConverter)

```python
c2doc = Chunk2Doc().setInputCols("ner_chunk").setOutputCol("ner_chunk_doc")
sbert_embedder = BertSentenceEmbeddings\
     .pretrained("sbiobert_base_cased_mli",'en','clinical/models')\
     .setInputCols(["ner_chunk_doc"])\
     .setOutputCol("sbert_embeddings")

snomed_ct_resolver = SentenceEntityResolverModel
 .pretrained("sbiobertresolve_snomed_findings","en", "clinical/models") \
 .setInputCols(["ner_chunk", "sbert_embeddings"]) \
 .setOutputCol("snomed_ct_code")\
 .setDistanceFunction("EUCLIDEAN")
 ```

Output:

|    | chunks                      |   begin |   end |      code | resolutions
|  2 | COPD  				 |     113 |   116 |  13645005 | copd - chronic obstructive pulmonary disease
|  8 | PTCA                        |     324 |   327 | 373108000 | post percutaneous transluminal coronary angioplasty (finding)
| 16 | close monitoring            |     519 |   534 | 417014005 | on examination - vigilance


See the [notebook](https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/3.Clinical_Entity_Resolvers.ipynb#scrollTo=VtDWAlnDList) for details.

#### 3. We are releasing the following pretrained clinical NER models:

ner_drugs_large   
(trained with medications dataset, and extracts drugs with the dosage, strength, form and route at once as a single entity; entities: drug)  
ner_deid_sd_large  
(extracts PHI entities, trained with augmented dataset)  
ner_anatomy_coarse  
(trained with enriched anatomy NER dataset; entities: anatomy)  
ner_anatomy_coarse_biobert  
chunkresolve_ICD10GM_2021 (German ICD10GM resolver)


We are also releasing two new NER models:

ner_aspect_based_sentiment  
(extracts positive, negative and neutral aspects about restaurants from the written feedback given by reviewers. )  
ner_financial_contract  
(extract financial entities from contracts. See the [notebook](https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/19.Financial_Contract_NER.ipynb) for details.)  


### 2.7.0

We are glad to announce that Spark NLP for Healthcare 2.7 has been released !

In this release, we introduce the following features:

#### 1. Text2SQL

Text2SQL Annotator that translates natural language text into SQL queries against a predefined database schema, which is one of the
most sought-after features of NLU. With the help of a pretrained text2SQL model, you will be able to query your database without writing a SQL query:

Example 1

Query:
What is the name of the nurse who has the most appointments?

Generated
SQL query from the model:

```sql
SELECT T1.Name  
FROM Nurse AS T1  
JOIN Appointment AS T2 ON T1.EmployeeID = T2.PrepNurse  
GROUP BY T2.prepnurse  
ORDER BY count(*) DESC  
LIMIT 1  
```

Response:  

|    | Name           |
|---:|:---------------|
|  0 | Carla Espinosa |

Example 2

Query:
How many patients do each physician take care of? List their names and number of patients they take care of.

Generated
SQL query from the model:

```sql
SELECT T1.Name,  
count(*)  
FROM Physician AS T1  
JOIN Patient AS T2 ON T1.EmployeeID = T2.PCP  
GROUP BY T1.Name  
```

Response:   

|    | Name             |   count(*) |
|---:|:-----------------|-----------:|
|  0 | Christopher Turk |          1 |
|  1 | Elliot Reid      |          2 |
|  2 | John Dorian      |          1 |


For now, it only comes with one pretrained model (trained on Spider
dataset) and new pretrained models will be released soon.

Check out the
Colab notebook to  see more examples and run on your data.


#### 2. SentenceEntityResolvers

In addition to ChunkEntityResolvers, we now release our first BioBert-based entity resolvers using the SentenceEntityResolver
annotator. It’s
fully trainable and comes with several pretrained entity resolvers for the following medical terminologies:

CPT: `biobertresolve_cpt`  
ICDO: `biobertresolve_icdo`  
ICD10CM: `biobertresolve_icd10cm`  
ICD10PCS: `biobertresolve_icd10pcs`  
LOINC: `biobertresolve_loinc`  
SNOMED_CT (findings): `biobertresolve_snomed_findings`  
SNOMED_INT (clinical_findings): `biobertresolve_snomed_findings_int`    
RXNORM (branded and clinical drugs): `biobertresolve_rxnorm_bdcd`  

Example:
```python
text = 'He has a starvation ketosis but nothing significant for dry oral mucosa'
df = get_icd10_codes (light_pipeline_icd10, 'icd10cm_code', text)
```

|    | chunks               |   begin |   end | code |
|---:|:---------------------|--------:|------:|:-------|
|  0 | a starvation ketosis |       7 |    26 | E71121 |                                                                                                                                                   
|  1 | dry oral mucosa      |      66 |    80 | K136   |


Check out the Colab notebook to  see more examples and run on your data.

You can also train your own entity resolver using any medical terminology like MedRa and UMLS. Check this notebook to
learn more about training from scratch.


#### 3. ChunkMerge Annotator

In order to use multiple NER models in the same pipeline, Spark NLP Healthcare has ChunkMerge Annotator that is used to return entities from each NER
model by overlapping. Now it has a new parameter to avoid merging overlapping entities (setMergeOverlapping)
to return all the entities regardless of char indices. It will be quite useful to analyze what every NER module returns on the same text.


#### 4. Starting SparkSession


We now support starting SparkSession with a different version of the open source jar and not only the one it was built
against by `sparknlp_jsl.start(secret, public="x.x.x")` for extreme cases.


#### 5. Biomedical NERs

We are releasing 3 new biomedical NER models trained with clinical embeddings (all one single entity models)  

`ner_bacterial_species` (comprising of Linneaus and Species800 datasets)  
`ner_chemicals` (general purpose and bio chemicals, comprising of BC4Chem and BN5CDR-Chem)  
`ner_diseases_large` (comprising of ner_disease, NCBI_Disease and BN5CDR-Disease)  

We are also releasing the biobert versions of the several clinical NER models stated below:  
`ner_clinical_biobert`  
`ner_anatomy_biobert`  
`ner_bionlp_biobert`  
`ner_cellular_biobert`  
`ner_deid_biobert`  
`ner_diseases_biobert`  
`ner_events_biobert`  
`ner_jsl_biobert`  
`ner_chemprot_biobert`  
`ner_human_phenotype_gene_biobert`  
`ner_human_phenotype_go_biobert`  
`ner_posology_biobert`  
`ner_risk_factors_biobert`  


Metrics (micro averages excluding O’s):

|    | model_name                        |   clinical_glove_micro |   biobert_micro |
|---:|:----------------------------------|-----------------------:|----------------:|
|  0 | ner_chemprot_clinical             |               0.816 |      0.803 |
|  1 | ner_bionlp                        |               0.748 |      0.808  |
|  2 | ner_deid_enriched                 |               0.934 |      0.918  |
|  3 | ner_posology                      |               0.915 |      0.911    |
|  4 | ner_events_clinical               |               0.801 |      0.809  |
|  5 | ner_clinical                      |               0.873 |      0.884  |
|  6 | ner_posology_small                |               0.941 |            |
|  7 | ner_human_phenotype_go_clinical   |               0.922 |      0.932  |
|  8 | ner_drugs                         |               0.964 |           |
|  9 | ner_human_phenotype_gene_clinical |               0.876 |      0.870  |
| 10 | ner_risk_factors                  |               0.728 |            |
| 11 | ner_cellular                      |               0.813 |      0.812  |
| 12 | ner_posology_large                |               0.921 |            |
| 13 | ner_anatomy                       |               0.851 |      0.831  |
| 14 | ner_deid_large                    |               0.942 |            |
| 15 | ner_diseases                      |               0.960 |      0.966  |


In addition to these, we release two new German NER models:

`ner_healthcare_slim` ('TIME_INFORMATION', 'MEDICAL_CONDITION',  'BODY_PART',  'TREATMENT', 'PERSON', 'BODY_PART')  
`ner_traffic` (extract entities regarding traffic accidents e.g. date, trigger, location etc.)  

#### 6. PICO Classifier

Successful evidence-based medicine (EBM) applications rely on answering clinical questions by analyzing large medical literature databases. In order to formulate
a well-defined, focused clinical question, a framework called PICO is widely used, which identifies the sentences in a given medical text that belong to the four components: Participants/Problem (P)  (e.g., diabetic patients), Intervention (I) (e.g., insulin),
Comparison (C) (e.g., placebo)  and Outcome (O) (e.g., blood glucose levels).

Spark NLP now introduces a pretrained PICO Classifier that
is trained with Biobert embeddings.

Example:

```python
text = “There appears to be no difference in smoking cessation effectiveness between 1mg and 0.5mg varenicline.”
pico_lp_pipeline.annotate(text)['class'][0]

ans: CONCLUSIONS
```

### 2.6.2

#### Overview
We are very happy to announce that version 2.6.2 of Spark NLP Enterprise is ready to be installed and used.
We are making available Named Entity Recognition, Sentence Classification and Entity Resolution models to analyze Adverse Drug Events in natural language text from clinical domains.

#### Models

##### NERs
We are pleased to announce that we have a brand new named entity recognition (NER) model for Adverse Drug Events (ADE) to extract ADE and DRUG entities from a given text.

ADE NER will have four versions in the library, trained with different size of word embeddings:

`ner_ade_bioert` (768d Bert embeddings)  
`ner_ade_clinicalbert` (768d Bert embeddings)  
`ner_ade_clinical` (200d clinical embeddings)  
`ner_ade_healthcare` (100d healthcare embeddings)  

More information and examples [here](https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/16.Adverse_Drug_Event_ADE_NER_and_Classifier.ipynb)

We are also releasing our first clinical pretrained classifier for ADE classification tasks. This new ADE classifier is trained on various ADE datasets, including the mentions in tweets to represent the daily life conversations as well. So it works well on the texts coming from academic context, social media and clinical notes. It’s trained with `Clinical Biobert` embeddings, which is the most powerful contextual language model in the clinical domain out there.

##### Classifiers
ADE classifier will have two versions in the library, trained with different Bert embeddings:

`classifierdl_ade_bioert` (768d BioBert embeddings)  
`classifierdl_adee_clinicalbert` (768d ClinicalBert embeddings)  

More information and examples [here](https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/16.Adverse_Drug_Event_ADE_NER_and_Classifier.ipynb)

##### Pipeline
By combining ADE NER and Classifier, we are releasing a new pretrained clinical pipeline for ADE tasks to save you from building pipelines from scratch. Pretrained pipelines are already fitted using certain annotators and transformers according to various use cases and you can use them as easy as follows:
```python
pipeline = PretrainedPipeline('explain_clinical_doc_ade', 'en', 'clinical/models')

pipeline.annotate('my string')
```
`explain_clinical_doc_ade` is bundled with `ner_ade_clinicalBert`, and `classifierdl_ade_clinicalBert`. It can extract ADE and DRUG clinical entities, and then assign ADE status to a text (`True` means ADE, `False` means not related to ADE).

More information and examples [here](https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/11.Pretrained_Clinical_Pipelines.ipynb)


##### Entity Resolver
We are releasing the first Entity Resolver for `Athena` (Automated Terminology Harmonization, Extraction and Normalization for Analytics, http://athena.ohdsi.org/) to extract concept ids via standardized medical vocabularies. For now, it only supports `conditions` section and can be used to map the clinical conditions with the corresponding standard terminology and then get the concept ids to store them in various database schemas.
It is named as `chunkresolve_athena_conditions_healthcare`.

We added slim versions of several clinical NER models that are trained with 100d healthcare word embeddings, which is lighter and smaller in size.

`ner_healthcare`
`assertion_dl_healthcare`
`ner_posology_healthcare`
`ner_events_healthcare`

##### Graph Builder
Spark NLP Licensed version has several DL based annotators (modules) such as NerDL, AssertionDL, RelationExtraction and GenericClassifier, and they are all based on Tensorflow (tf) with custom graphs. In order to make the creating and customizing the tf graphs for these models easier for our licensed users, we added a graph builder to the Python side of the library. Now you can customize your graphs and use them in the respected models while training a new DL model.

```python
from sparknlp_jsl.training import tf_graph

tf_graph.build("relation_extraction",build_params={"input_dim": 6000, "output_dim": 3, 'batch_norm':1, "hidden_layers": [300, 200], "hidden_act": "relu", 'hidden_act_l2':1}, model_location=".", model_filename="re_with_BN")
```
More information and examples [here](https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/17.Graph_builder_for_DL_models.ipynb)


### 2.6.0

#### Overview

We are honored to announce that Spark NLP Enterprise 2.6.0 has been released.
The first time ever, we release three pretrained clinical pipelines to save you from building pipelines from scratch. Pretrained pipelines are already fitted using certain annotators and transformers according to various use cases.
The first time ever, we are releasing 3 licensed German models for healthcare and Legal domains.

</div><div class="h3-box" markdown="1">

#### Models

##### Pretrained Pipelines:

The first time ever, we release three pretrained clinical pipelines to save you from building pipelines from scratch.
Pretrained pipelines are already fitted using certain annotators and transformers according to various use cases and you can use them as easy as follows:

```python
pipeline = PretrainedPipeline('explain_clinical_doc_carp', 'en', 'clinical/models')

pipeline.annotate('my string')
```

Pipeline descriptions:

- ```explain_clinical_doc_carp``` a pipeline with ner_clinical, assertion_dl, re_clinical and ner_posology. It will extract clinical and medication entities, assign assertion status and find relationships between clinical entities.

- ```explain_clinical_doc_era``` a pipeline with ner_clinical_events, assertion_dl and re_temporal_events_clinical. It will extract clinical entities, assign assertion status and find temporal relationships between clinical entities.

- ```recognize_entities_posology``` a pipeline with ner_posology. It will only extract medication entities.

More information and examples are available here: https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/11.Pretrained_Clinical_Pipelines.ipynb.

</div><div class="h3-box" markdown="1">

#### Pretrained Named Entity Recognition and Relationship Extraction Models (English)

RE models:

```
re_temporal_events_clinical
re_temporal_events_enriched_clinical
re_human_phenotype_gene_clinical
re_drug_drug_interaction_clinical
re_chemprot_clinical
```
NER models:

```
ner_human_phenotype_gene_clinical
ner_human_phenotype_go_clinical
ner_chemprot_clinical
```
More information and examples here:
https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/10.Clinical_Relation_Extraction.ipynb

</div><div class="h3-box" markdown="1">

#### Pretrained Named Entity Recognition and Relationship Extraction Models (German)

The first time ever, we are releasing 3 licensed German models for healthcare and Legal domains.

- ```German Clinical NER``` model for 19 clinical entities

- ```German Legal NER``` model for 19 legal entities

- ```German ICD-10GM```

More information and examples here:

https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/14.German_Healthcare_Models.ipynb

https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/15.German_Legal_Model.ipynb

</div><div class="h3-box" markdown="1">

#### Other Pretrained Models

We now have Named Entity Disambiguation model out of the box.

Disambiguation models map words of interest, such as names of persons, locations and companies, from an input text document to corresponding unique entities in a target Knowledge Base (KB).

https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/12.Named_Entity_Disambiguation.ipynb

Due to ongoing requests about Clinical Entity Resolvers, we release a notebook to let you see how to train an entity resolver using an open source dataset based on Snomed.

https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/13.Snomed_Entity_Resolver_Model_Training.ipynb

</div><div class="h3-box" markdown="1">

### 2.5.5

#### Overview

We are very happy to release Spark NLP for Healthcare 2.5.5 with a new state-of-the-art RelationExtraction annotator to identify relationships between entities coming from our pretrained NER models.
This is also the first release to support Relation Extraction with the following two (2) models: `re_clinical` and `re_posology` in the `clinical/models` repository.
We also include multiple bug fixes as usual.

</div><div class="h3-box" markdown="1">

#### New Features

* RelationExtraction annotator that receives `WORD_EMBEDDINGS`, `POS`, `CHUNK`, `DEPENDENCY` and returns the CATEGORY of the relationship and a confidence score.

</div><div class="h3-box" markdown="1">

#### Enhancements

* AssertionDL Annotator now keeps logs of the metrics while training
* DeIdentification now has a default behavior of merging entities close in Levenshtein distance with `setConsistentObfuscation` and `setSameEntityThreshold` params.
* DeIdentification now has a specific parameter `setObfuscateDate` to obfuscate dates (which will be otherwise just masked). The only formats obfuscated when the param is true will be the ones present in `dateFormats` param.
* NerConverterInternal now has a `greedyMode` param that will merge all contiguous tags of the same type regardless of boundary tags like "B","E","S".
* AnnotationToolJsonReader includes `mergeOverlapping` parameter to merge (or not) overlapping entities from the Annotator jsons i.e. not included in the assertion list.

</div><div class="h3-box" markdown="1">

#### Bugfixes

* DeIdentification documentation bug fix (typo)
* DeIdentification training bug fix in obfuscation dictionary
* IOBTagger now has the correct output type `NAMED_ENTITY`

</div><div class="h3-box" markdown="1">

#### Deprecations

* EnsembleEntityResolver has been deprecated

Models

* We have 2 new `english` Relationship Extraction model for Clinical and Posology NERs:
   - `re_clinical`: with `ner_clinical` and `embeddings_clinical`
   - `re_posology`: with `ner_posology` and `embeddings_clinical`

</div><div class="h3-box" markdown="1">

### 2.5.3

#### Overview

We are pleased to announce the release of Spark NLP for Healthcare 2.5.3.
This time we include four (4) new Annotators: FeatureAssembler, GenericClassifier, Yake Keyword Extractor and NerConverterInternal.
We also include helper classes to read datasets from CodiEsp and Cantemist Spanish NER Challenges.
This is also the first release to support the following models: `ner_diag_proc` (spanish), `ner_neoplasms` (spanish), `ner_deid_enriched` (english).
We have also included Bugifxes and Enhancements for AnnotationToolJsonReader and ChunkMergeModel.

</div><div class="h3-box" markdown="1">

#### New Features

* FeatureAssembler Transformer: Receives a list of column names containing numerical arrays and concatenates them to form one single `feature_vector` annotation
* GenericClassifier Annotator: Receives a `feature_vector` annotation and outputs a `category` annotation
* Yake Keyword Extraction Annotator: Receives a `token` annotation and outputs multi-token `keyword` annotations
* NerConverterInternal Annotator: Similar to it's open source counterpart in functionality, performs smarter extraction for complex tokenizations and confidence calculation
* Readers for CodiEsp and Cantemist Challenges

</div><div class="h3-box" markdown="1">

#### Enhancements

* AnnotationToolJsonReader includes parameter for preprocessing pipeline (from Document Assembling to Tokenization)
* AnnotationToolJsonReader includes parameter to discard specific entity types

</div><div class="h3-box" markdown="1">

#### Bugfixes

* ChunkMergeModel now prioritizes highest number of different entities when coverage is the same

</div><div class="h3-box" markdown="1">

#### Models

* We have 2 new `spanish` models for Clinical Entity Recognition: `ner_diag_proc` and `ner_neoplasms`
* We have a new `english` Named Entity Recognition model for deidentification: `ner_deid_enriched`

</div><div class="h3-box" markdown="1">

### 2.5.2

#### Overview

We are really happy to bring you Spark NLP for Healthcare 2.5.2, with a couple new features and several enhancements in our existing annotators.
This release was mainly dedicated to generate adoption in our AnnotationToolJsonReader, a connector that provide out-of-the-box support for out Annotation Tool and our practices.
Also the ChunkMerge annotator has ben provided with extra functionality to remove entire entity types and to modify some chunk's entity type
We also dedicated some time in finalizing some refactorization in DeIdentification annotator, mainly improving type consistency and case insensitive entity dictionary for obfuscation.
Thanks to the community for all the feedback and suggestions, it's really comfortable to navigate together towards common functional goals that keep us agile in the SotA.

</div><div class="h3-box" markdown="1">

#### New Features

* Brand new IOBTagger Annotator
* NerDL Metrics provides an intuitive DataFrame API to calculate NER metrics at tag (token) and entity (chunk) level

</div><div class="h3-box" markdown="1">

#### Enhancements

* AnnotationToolJsonReader includes parameters for document cleanup, sentence boundaries and tokenizer split chars
* AnnotationToolJsonReader uses the task title if present and uses IOBTagger annotator
* AnnotationToolJsonReader has improved alignment in assertion train set generation by using an `alignTol` parameter as tollerance in chunk char alignment
* DeIdentification refactorization: Improved typing and replacement logic, case insensitive entities for obfuscation
* ChunkMerge Annotator now handles:
 - Drop all chunks for an entity
 - Replace entity name
 - Change entity type for a specific (chunk, entity) pair
 - Drop specific (chunk, entity) pairs
* `caseSensitive` param to EnsembleEntityResolver
* Output logs for AssertionDLApproach loss
* Disambiguator is back with improved dependency management

</div><div class="h3-box" markdown="1">

#### Bugfixes

* Bugfix in python when Annotators shared domain parts across public and internal
* Bugfix in python when ChunkMerge annotator was loaded from disk
* ChunkMerge now weights the token coverage correctly when multiple multi-token entities overlap

</div><div class="h3-box" markdown="1">

### 2.5.0

#### Overview

We are happy to bring you Spark NLP for Healthcare 2.5.0 with new Annotators, Models and Data Readers.
Model composition and iteration is now faster with readers and annotators designed for real world tasks.
We introduce ChunkMerge annotator to combine all CHUNKS extracted by different Entity Extraction Annotators.
We also introduce an Annotation Reader for JSL AI Platform's Annotation Tool.
This release is also the first one to support the models: `ner_large_clinical`, `ner_events_clinical`, `assertion_dl_large`, `chunkresolve_loinc_clinical`, `deidentify_large`
And of course we have fixed some bugs.

</div><div class="h3-box" markdown="1">

#### New Features

* AnnotationToolJsonReader is a new class that imports a JSON from AI Platform's Annotation Tool an generates NER and Assertion training datasets
* ChunkMerge Annotator is a new functionality that merges two columns of CHUNKs handling overlaps with a very straightforward logic: max coverage, max # entities
* ChunkMerge Annotator handles inputs from NerDLModel, RegexMatcher, ContextualParser, TextMatcher
* A DeIdentification pretrained model can now work in 'mask' or 'obfuscate' mode

</div><div class="h3-box" markdown="1">

#### Enhancements

* DeIdentification Annotator has a more consistent API:
    * `mode` param with values ('mask'l'obfuscate') to drive its behavior
    * `dateFormats` param a list of string values to to select which `dateFormats` to obfuscate (and which to just mask)
* DeIdentification Annotator no longer automatically obfuscates dates. Obfuscation is now driven by `mode` and `dateFormats` params
* A DeIdentification pretrained model can now work in 'mask' or 'obfuscate' mode

</div><div class="h3-box" markdown="1">

#### Bugfixes

* DeIdentification Annotator now correctly deduplicates protected entities coming from NER / Regex
* DeIdentification Annotator now indexes chunks correctly after merging them
* AssertionDLApproach Annotator can now be trained with the graph in any folder specified by setting `graphFolder` param
* AssertionDLApproach now has the `setClasses` param setter in Python wrapper
* JVM Memory and Kryo Max Buffer size increased to 32G and 2000M respectively in `sparknlp_jsl.start(secret)` function

</div><div class="h3-box" markdown="1">

### 2.4.6

#### Overview

We release Spark NLP for Healthcare 2.4.6 to fix some minor bugs.

</div><div class="h3-box" markdown="1">

#### Bugfixes

* Updated IDF value calculation to be probabilistic based log[(N - df_t) / df_t + 1] as opposed to log[N / df_t]
* TFIDF cosine distance was being calculated with the rooted norms rather than with the original squared norms
* Validation of label cols is now performed at the beginning of EnsembleEntityResolver
* Environment Variable for License value named jsl.settings.license
* Now DocumentLogRegClassifier can be serialized from Python (bug introduced with the implementation of RecursivePipelines, LazyAnnotator attribute)

</div><div class="h3-box" markdown="1">

### 2.4.5

#### Overview

We are glad to announce Spark NLP for Healthcare 2.4.5. As a new feature we are happy to introduce our new EnsembleEntityResolver which allows our Entity Resolution architecture to scale up in multiple orders of magnitude and handle datasets of millions of records on a sub-log computation increase
We also enhanced our ChunkEntityResolverModel with 5 new distance calculations with weighting-array and aggregation-strategy params that results in more levers to finetune its performance against a given dataset.

</div><div class="h3-box" markdown="1">

#### New Features

* EnsembleEntityResolver consisting of an integrated TFIDF-Logreg classifier in the first layer + Multiple ChunkEntityResolvers in the second layer (one per each class)
* Five (5) new distances calculations for ChunkEntityResolver, namely:
    - Token Based: TFIDF-Cosine, Jaccard, SorensenDice
    - Character Based: JaroWinkler and Levenshtein
* Weight parameter that works as a multiplier for each distance result to be considered during their aggregation
* Three (3) aggregation strategies for the enabled distance in a particular instance, namely: AVERAGE, MAX and MIN

</div><div class="h3-box" markdown="1">

#### Enhancements

* ChunkEntityResolver can now compute distances over all the `neighbours` found and return the metadata just for the best `alternatives` that meet the `threshold`;
before it would calculate them over the neighbours and return them all in the metadata
* ChunkEntityResolver now has an `extramassPenalty` parameter to accoun for penalization of token-length difference in compared strings
* Metadata for the ChunkEntityResolver has been updated accordingly to reflect all new features
* StringDistances class has been included in utils to aid in the calculation and organization of different types of distances for Strings
* HasFeaturesJsl trait has been included to support the serialization of Features including [T] <: AnnotatorModel[T] types

</div><div class="h3-box" markdown="1">

#### Bugfixes

* Frequency calculation for WMD in ChunkEntityResolver has been adjusted to account for real word count representation
* AnnotatorType for DocumentLogRegClassifier has been changed to CATEGORY to align with classifiers in Open Source library

</div><div class="h3-box" markdown="1">

#### Deprecations

* Legacy EntityResolver{Approach, Model} classes have been deprecated in favor of ChunkEntityResolver classes
* ChunkEntityResolverSelector classes has been deprecated in favor of EnsembleEntityResolver

</div><div class="h3-box" markdown="1">

### 2.4.2

#### Overview

We are glad to announce Spark NLP for Healthcare 2.4.2. As a new feature we are happy to introduce our new Disambiguation Annotator,
which will let the users resolve different kind of entities based on Knowledge bases provided in the form of Records in a RocksDB database.
We also enhanced / fixed DocumentLogRegClassifier, ChunkEntityResolverModel and ChunkEntityResolverSelector Annotators.

</div><div class="h3-box" markdown="1">

#### New Features

* Disambiguation Annotator (NerDisambiguator and NerDisambiguatorModel) which accepts annotator types CHUNK and SENTENCE_EMBEDDINGS and
returns DISAMBIGUATION annotator type. This output annotation type includes all the matches in the result and their similarity scores in the metadata.

</div><div class="h3-box" markdown="1">

#### Enhancements

* ChunkEntityResolver Annotator now supports both EUCLIDEAN and COSINE distance for the KNN search and WMD calculation.

</div><div class="h3-box" markdown="1">

#### Bugfixes

* Fixed a bug in DocumentLogRegClassifier Annotator to support its serialization to disk.
* Fixed a bug in ChunkEntityResolverSelector Annotator to group by both SENTENCE and CHUNK at the time of forwarding tokens and embeddings to the lazy annotators.
* Fixed a bug in ChunkEntityResolverModel in which the same exact embeddings was not included in the neighbours.

</div><div class="h3-box" markdown="1">

### 2.4.1

#### Overview

Introducing Spark NLP for Healthcare 2.4.1 after all the feedback we received in the form of issues and suggestions on our different communication channels.
Even though 2.4.0 was very stable, version 2.4.1 is here to address minor bug fixes that we summarize in the following lines.

</div><div class="h3-box" markdown="1">

#### Bugfixes

* Changing the license Spark property key to be "jsl" instead of "sparkjsl" as the latter generates inconsistencies
* Fix the alignment logic for tokens and chunks in the ChunkEntityResolverSelector because when tokens and chunks did not have the same begin-end indexes the resolution was not executed

</div><div class="h3-box" markdown="1">

### 2.4.0

#### Overview

We are glad to announce Spark NLP for Healthcare 2.4.0. This is an important release because of several refactorizations achieved in the core library, plus the introduction of several state of the art algorithms, new features and enhancements.
We have included several architecture and performance improvements, that aim towards making the library more robust in terms of storage handling for Big Data.
In the NLP aspect, we have introduced a ContextualParser, DocumentLogRegClassifier and a ChunkEntityResolverSelector.
These last two Annotators also target performance time and memory consumption by lowering the order of computation and data loaded to memory in each step when designed following a hierarchical pattern.
We have put a big effort on this one, so please enjoy and share your comments. Your words are always welcome through all our different channels.
Thank you very much for your important doubts, bug reports and feedback; they are always welcome and much appreciated.

</div><div class="h3-box" markdown="1">

#### New Features

* BigChunkEntityResolver Annotator: New experimental approach to reduce memory consumption at expense of disk IO.
* ContextualParser Annotator: New entity parser that works based on context parameters defined in a JSON file.
* ChunkEntityResolverSelector Annotator: New AnnotatorModel that takes advantage of the RecursivePipelineModel + LazyAnnotator pattern to annotate with different LazyAnnotators at runtime.
* DocumentLogregClassifier Annotator: New Annotator that provides a wrapped TFIDF Vectorizer + LogReg Classifier for TOKEN AnnotatorTypes (either at Document level or Chunk level)

</div><div class="h3-box" markdown="1">

#### Enhancements

* `normalizedColumn` Param is no longer required in ChunkEntityResolver Annotator (defaults to the `labelCol` Param value).
* ChunkEntityResolverMetadata now has more data to infer whether the match is meaningful or not.

</div><div class="h3-box" markdown="1">

#### Bugfixes

* Fixed a bug on ContextSpellChecker Annotator where unrecognized tokens would cause an exception if not in vocabulary.
* Fixed a bug on ChunkEntityResolver Annotator where undetermined results were coming out of negligible confidence scores for matches.
* Fixed a bug on ChunkEntityResolver Annotator where search would fail if the `neighbours` Param was grater than the number of nodes in the tree. Now it returns up to the number of nodes in the tree.

</div><div class="h3-box" markdown="1">

#### Deprecations

* OCR Moves to its own JSL Spark OCR project.

</div>

#### Infrastructure

* Spark NLP License is now required to utilize the library. Please follow the instructions on the shared email.
