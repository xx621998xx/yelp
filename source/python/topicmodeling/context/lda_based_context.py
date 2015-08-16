import time
import operator
from gensim import corpora
from gensim.models import ldamodel
from topicmodeling.context import lda_context_utils
from topicmodeling.context import context_utils
from topicmodeling.context import reviews_clusterer
from topicmodeling.context.review import Review


__author__ = 'fpena'


class LdaBasedContext:

    def __init__(self, reviews=None, text_reviews=None):
        self.text_reviews = text_reviews
        self.alpha = 0.005
        self.beta = 1.0
        self.reviews = reviews
        self.specific_reviews = None
        self.generic_reviews = None
        self.all_nouns = None
        self.all_senses = None
        self.sense_groups = None
        self.review_topics_list = None
        self.num_topics = 150
        self.topics = range(self.num_topics)
        self.topic_model = None

    def init_reviews(self):
        if not self.reviews:
            self.init_from_text(self.text_reviews)
        self.cluster()

    def init_from_text(self, text_reviews):
        self.text_reviews = text_reviews

        index = 0
        print('num_reviews', len(self.text_reviews))
        for text_review in self.text_reviews:
            self.reviews.append(Review(text_review))
            print('index', index)
            index += 1

    def cluster(self):

        print('cluster reviews', time.strftime("%H:%M:%S"))

        cluster_labels = reviews_clusterer.cluster_reviews(self.reviews)
        review_clusters =\
            reviews_clusterer.split_list_by_labels(self.reviews, cluster_labels)
        # print(cluster_labels)

        self.specific_reviews = review_clusters[0]
        self.generic_reviews = review_clusters[1]

        print('cluster reviews', time.strftime("%H:%M:%S"))

    def filter_topics(self):

        specific_reviews_text =\
            context_utils.get_text_from_reviews(self.specific_reviews)
        generic_reviews_text =\
            context_utils.get_text_from_reviews(self.generic_reviews)

        specific_bag_of_words =\
            lda_context_utils.create_bag_of_words(specific_reviews_text)
        generic_bag_of_words =\
            lda_context_utils.create_bag_of_words(generic_reviews_text)

        dictionary = corpora.Dictionary(specific_bag_of_words)
        dictionary.filter_extremes(2, 0.6)

        # dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in specific_bag_of_words]
        self.topic_model = ldamodel.LdaModel(
            corpus, id2word=dictionary, num_topics=self.num_topics)

        print('created topic model', time.strftime("%H:%M:%S"))

        specific_corpora =\
            [dictionary.doc2bow(text) for text in specific_bag_of_words]
        generic_corpora =\
            [dictionary.doc2bow(text) for text in generic_bag_of_words]

        print('created bag of words', time.strftime("%H:%M:%S"))

        lda_context_utils.update_reviews_with_topics(
            self.topic_model, specific_corpora, self.specific_reviews)
        lda_context_utils.update_reviews_with_topics(
            self.topic_model, generic_corpora, self.generic_reviews)

        print('updated reviews with topics', time.strftime("%H:%M:%S"))

        topic_ratio_map = {}

        for topic in range(self.num_topics):
            specific_weighted_frq = \
                lda_context_utils.calculate_topic_weighted_frequency(
                    topic, self.specific_reviews)
            generic_weighted_frq = \
                lda_context_utils.calculate_topic_weighted_frequency(
                    topic, self.generic_reviews)

            if (generic_weighted_frq < self.alpha or
                    specific_weighted_frq < self.alpha):
                self.topics.remove(topic)
                continue

            ratio = specific_weighted_frq / generic_weighted_frq

            # if ratio < self.beta:
            #     self.topics.remove(topic)
            #     continue

            topic_ratio_map[topic] = ratio

        sorted_topics = sorted(
            topic_ratio_map.items(), key=operator.itemgetter(1), reverse=True)

        # for topic in topic_model.show_topics(num_topics=self.num_topics):
        #     print(topic)
        print('num_topics', len(self.topics), time.strftime("%H:%M:%S"))

        # for topic in sorted_topics:
        # for i in range(topic_model.num_topics):
            # print('topic', i, topic_model.print_topic(i, topn=50))
            # topic_index = topic[0]
            # ratio = topic[1]
            # print('topic', ratio, topic_index, self.topic_model.print_topic(topic_index, topn=50))

        return sorted_topics


def main():
    reviews_file = "/Users/fpena/tmp/yelp_training_set/yelp_training_set_review_hotels.json"
    my_reviews = context_utils.load_reviews(reviews_file)
    print("reviews:", len(my_reviews))

    # lda_context_utils.discover_topics(my_reviews, 150)
    lda_based_context = LdaBasedContext()
    lda_based_context.init_from_text(my_reviews)
    my_topics = lda_based_context.filter_topics()
    print(my_topics)

# start = time.time()
# main()
# end = time.time()
# total_time = end - start
# print("Total time = %f seconds" % total_time)
