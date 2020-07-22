"""
Short unit tests to make sure our dataset readers are behaving correctly.
Checks a sample from the scierc data and the ACE event data.
"""

import itertools
import os
from allennlp.common.testing import AllenNlpTestCase
from allennlp.common.util import ensure_list
from allennlp.data.vocabulary import Vocabulary

from dygie.data import DyGIEReader

import unittest
import os


class TestDygieReader(AllenNlpTestCase):

    def setUp(self):
        # scierc
        # Sentence lengths: [20, 23, 36, 14, 14, 30, 31, 15].
        # Cumulative sentence lengths: [20, 43, 79, 93, 107, 137, 168, 183].
        self.reader = DyGIEReader(max_span_width=5)
        self.dataset = self.reader.read(str("/Users/kennychen/dygiepp/dygie/tests/fixtures/scierc_article.json"))
        #self.ds = self.reader._read(str("/Users/kennychen/dygiepp/dygie/tests/fixtures/scierc_article.json"))

    def tearDown(self):
        pass

    def test_tokens_correct_scierc(self):
        # instances are now entire documents instead of sentences
        instance = self.dataset.instances[0]
        tokens = instance["text"][3][0:]
        assert len(tokens) == 14
        text = [token.text for token in tokens]
        assert text[:6] == ["Thirdly", "the", "learned", "intrinsic", "object", "structure"]

    def test_ner_correct_scierc(self):
        instance = self.dataset.instances[0]
        ner_field = instance["ner_labels"][3]
        spans = instance["spans"][3]

        for label, span in zip(ner_field, spans):
            start, end = span.span_start, span.span_end
            if start == 2 and end == 3:
                assert label.label == "Method"
            elif start == 11 and end == 12:
                assert label.label == "Method"
            else:
                assert label.label == ""

        # for label, span in zip(ner_field.labels, ner_field.sequence_field.field_list):
        #     start, end = span.span_start, span.span_end
        #     if start == 3 and end == 5:
        #         assert label == "OtherScientificTerm"
        #     elif start == 10 and end == 12:
        #         assert label == "Method"
        #     else:
        #         assert label == ""

    def test_relation_correct_scierc(self):
        instance = self.dataset.instances[0]
        relation_field = instance["relation_labels"][5]
        span_list = relation_field.sequence_field
        # There should be one relation in this sentence,
        indices = relation_field.indices
        labels = relation_field.labels
        assert len(indices) == len(labels) == 1
        ix = indices[0]
        label = labels[0]
        # Check that the relation refers to the correct spans
        span1 = span_list[ix[0]]
        span2 = span_list[ix[1]]
        assert ((span1.span_start == 19 and span1.span_end == 20 and
                 span2.span_start == 22 and span2.span_end == 24))
        # Check that the label's correct.
        assert label == "USED-FOR"

    def test_coref_correct_scierc(self):
        instance = self.dataset.instances[0]
        coref_field = instance["coref_labels"]
        spans = instance["spans"]
        # A list, one entry per sentence. For each sentence, a dict mapping spans to cluster id's.
        cluster_mappings = [{(6, 6): 1},
                            {},
                            {(19, 21): 0},
                            {(11, 12): 0, (2, 3): 2},
                            {(3, 5): 0},
                            {(5, 7): 0, (19, 20): 2, (22, 24): 3},
                            {(5, 5): 3},
                            {(2, 2): 1}]
        for instance, cluster_mapping, span in zip(coref_field, cluster_mappings, spans):
            curr_coref_field = instance
            curr_span = span
            for label, span in zip(curr_coref_field, curr_span):
                start, end = span.span_start, span.span_end
                if (start, end) in cluster_mapping:
                    # print(start, end)
                    # print(label.label)
                    assert cluster_mapping[(start, end)] == label.label
                else:
                    assert label.label == -1


    def test_vocab_size_correct_scierc(self):
       vocab = Vocabulary.from_instances(self.instances_scierc)
       # There are 4 unique NER labels and 6 relation labels in the text fixture doc. For the ner
       # labels, there is an extra category for the null label. For the relation labels, there
       # isn't. This is due to the way their respective `Field`s represent labels.
       assert vocab.get_vocab_size("ner_labels") == 5
       assert vocab.get_vocab_size("relation_labels") == 6
       # For numeric labels, vocab size is 0.
       assert vocab.get_vocab_size("coref_labels") == 0



if __name__ == "__main__":
    test = TestDygieReader()
    test.setUp()
    instance = test.dataset.instances[0]
    coref_field = instance["coref_labels"]
    spans = instance["spans"]

    test.test_coref_correct_scierc()
# test.test_ner_correct_scierc()
    #test.test_relation_correct_scierc()
    #test.test_tokens_correct_scierc()


#
#
#    def test_relation_correct_scierc(self):
#        instance = self.instances_scierc[5]
#        relation_field = instance["relation_labels"]
#        span_list = relation_field.sequence_field.field_list
#        # There should be one relation in this sentence,
#        indices = relation_field.indices
#        labels = relation_field.labels
#        assert len(indices) == len(labels) == 1
#        ix = indices[0]
#        label = labels[0]
#        # Check that the relation refers to the correct spans
#        span1 = span_list[ix[0]]
#        span2 = span_list[ix[1]]
#        assert ((span1.span_start == 19 and span1.span_end == 20 and
#                 span2.span_start == 22 and span2.span_end == 24))
#        # Check that the label's correct.
#        assert label == "USED-FOR"
#
#    def test_vocab_size_correct_scierc(self):
#        vocab = Vocabulary.from_instances(self.instances_scierc)
#        # There are 4 unique NER labels and 6 relation labels in the text fixture doc. For the ner
#        # labels, there is an extra category for the null label. For the relation labels, there
#        # isn't. This is due to the way their respective `Field`s represent labels.
#        assert vocab.get_vocab_size("ner_labels") == 5
#        assert vocab.get_vocab_size("relation_labels") == 6
#        # For numeric labels, vocab size is 0.
#        assert vocab.get_vocab_size("coref_labels") == 0
#
#    def test_ner_correct_ace(self):
#        # Tests that ACE events get read in correctly.
#        instance = self.instances_ace[57]
#        # A couple spot checks on ner.
#        ner_field = instance["ner_labels"]
#        assert sum([x != "" for x in ner_field]) == 11
#        for label, span in zip(ner_field.labels, ner_field.sequence_field.field_list):
#            start, end = span.span_start, span.span_end
#            if start == 5 and end == 6:
#                assert label == "PER"
#            if start == 27 and end == 28:
#                assert label == "GPE"
#
#    def test_triggers_correct_ace(self):
#        # Check the event triggers.
#        instance = self.instances_ace[57]
#        trigger_field = instance["trigger_labels"]
#        for i, label in enumerate(trigger_field.labels):
#            if i == 16:
#                assert label == "conflict_attack"
#            else:
#                assert label == ""
#
#    def test_event_arguments_correct_ace(self):
#        # Check the event arguments.
#        instance = self.instances_ace[57]
#        argument_field = instance["argument_labels"]
#        span_list = argument_field.col_field.field_list
#        indices = argument_field.indices
#        labels = argument_field.labels
#        assert len(indices) == len(labels) == 4
#        expected_results = {(18, 21): "attacker",
#                            (37, 37): "place",
#                            (5, 6): "target",
#                            (9, 13): "target"}
#        for ix, label in zip(indices, labels):
#            # All the arguments should have the same trigger, at position 16.
#            trigger_ix = ix[0]
#            argument_span_ix = span_list[ix[1]]
#            argument_span = (argument_span_ix.span_start, argument_span_ix.span_end)
#            assert argument_span in expected_results
#            # All argument have the same trigger.
#            assert 16 == trigger_ix
#            # Check that arguments have correct labels.
#            assert label == expected_results[argument_span]
