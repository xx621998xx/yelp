from abc import ABCMeta, abstractmethod
from tripadvisor.fourcity import extractor
from tripadvisor.fourcity import fourcity_clusterer

__author__ = 'fpena'


class MultiCriteriaBaseRecommender(object):

    __metaclass__ = ABCMeta

    def __init__(
            self, name, similarity_metric='euclidean',
            significant_criteria_ranges=None):
        self._name = name
        self.similarity_metric = similarity_metric
        self.significant_criteria_ranges = significant_criteria_ranges
        self.reviews = None
        self.user_ids = None
        self.user_dictionary = None
        self.user_cluster_dictionary = None
        self.user_similarity_matrix = None

    def load(self, reviews):
        self.reviews = reviews
        self.user_dictionary =\
            extractor.initialize_users(self.reviews, self.significant_criteria_ranges)
        self.user_cluster_dictionary = fourcity_clusterer.build_user_clusters(
            self.reviews, self.significant_criteria_ranges)
        self.user_ids = extractor.get_groupby_list(self.reviews, 'user_id')
        self.user_similarity_matrix =\
            fourcity_clusterer.build_user_similarities_matrix(
                self.user_ids, self.user_dictionary, self.similarity_metric)

    def clear(self):
        self.reviews = None
        self.user_ids = None
        self.user_dictionary = None
        self.user_cluster_dictionary = None
        self.user_similarity_matrix = None

    @abstractmethod
    def predict_rating(self, user, item):
        pass

    @property
    def name(self):
        return self._name