import pandas as pd
import numpy as np
import pickle
import importlib
import logging
import json
import mysql.connector
import multiprocessing
from scipy import spatial
from gensim.models import word2vec

vector_size = 500
config = importlib.import_module("config")


def avg_feature_vector(model, words, num_features):
    featureVec = np.zeros((num_features,), dtype="float32")
    nwords = 0
    index2word_set = set(model.wv.index_to_key)
    for word in words:
        if word in index2word_set:
            nwords = nwords+1
            featureVec = np.add(featureVec, model.wv[word])
    if (nwords > 0):
        featureVec = np.divide(featureVec, nwords)
    return featureVec


def sum_feature_vector(model, words, num_features):
    featureVec = np.zeros((num_features,), dtype="float32")
    nwords = 0
    index2word_set = set(model.wv.index_to_key)
    for word in words:
        if word in index2word_set:
            nwords = nwords+1
            featureVec = np.add(featureVec, model.wv[word])
    return featureVec


def compare_two_list_skills(model, skills_1, skills_2):
    sentence_1_avg_vector = avg_feature_vector(
        model, skills_1, num_features=vector_size)
    sentence_2_avg_vector = avg_feature_vector(
        model, skills_2, num_features=vector_size)
    sen1_sen2_similarity = 1 - \
        spatial.distance.cosine(sentence_1_avg_vector, sentence_2_avg_vector)
    return sen1_sen2_similarity


def compare_two_list_skills_sum(model, skills_1, skills_2):
    sentence_1_avg_vector = sum_feature_vector(
        model, skills_1, num_features=vector_size)
    sentence_2_avg_vector = sum_feature_vector(
        model, skills_2, num_features=vector_size)
    sen1_sen2_similarity = 1 - \
        spatial.distance.cosine(sentence_1_avg_vector, sentence_2_avg_vector)
    return sen1_sen2_similarity


def get_most_smilar_skills(model, skills, topn):
    all_skills = model.wv.index_to_key
    valid_skills = []
    for skill in skills:
        if skill in all_skills:
            valid_skills.append(skill)
    if len(valid_skills) == 0:
        return []
    other_skills = []
    for skill in config.popular_skills:
        if skill not in valid_skills:
            other_skills.append(skill)
    primary_skills_avg_vector = avg_feature_vector(
        model, valid_skills, num_features=vector_size)
    possibilities = {}
    for skill in other_skills:
        skill_vector = model.wv[skill]
        possibilities[skill] = 1 - \
            spatial.distance.cosine(primary_skills_avg_vector, skill_vector)
    top_n_skills = []
    i = 0
    for skill in dict(sorted(possibilities.items(), key=lambda item: item[1], reverse=True)):
        if i < topn:
            top_n_skills.append(skill)
        i = i + 1

    return top_n_skills


def train_model():
    skills_list = []
    words = []
    dataBase = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="upwork"
    )
    db_cursor = dataBase.cursor()
    sql_query = ("SELECT skills FROM skills")
    db_cursor.execute(sql_query)
    query_result = db_cursor.fetchall()
    length = 0
    for i in range(len(query_result)):
        skills = json.loads(query_result[i][0])
        skills.sort()
        if (len(skills) < 3):
            continue
        if skills in skills_list:
            continue
        length += len(skills)
        for j in range(len(skills)):
            if skills[j] not in words:
                words.append(skills[j])
        skills_list.append(skills)
    length = length / len(skills_list)
    dataBase.close()
    # logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    model = word2vec.Word2Vec(skills_list,
                              workers=multiprocessing.cpu_count(),
                              vector_size=vector_size,
                              min_count=3,
                              window=6,
                              sample=1e-3,
                              epochs=10,
                              sg=1
                              )
    model.init_sims(replace=True)
    model.save("word2vec.model")

    print("average length is: ", length)
    print("total lists count: ", len(skills_list))
    print("total words count: ", len(words))
    print("saved words count: ", len(model.wv.index_to_key))


if __name__ == "__main__":
    train_model()
