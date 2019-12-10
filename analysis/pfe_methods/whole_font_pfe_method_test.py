"""Unit tests for the whole_font_pfe_method module."""

import unittest
from analysis import font_loader
from analysis import request_graph
from analysis.pfe_methods import whole_font_pfe_method

ROBOTO_REGULAR_WOFF2_SIZE = 64736
ROBOTO_THIN_WOFF2_SIZE = 62908


class WholeFontPfeMethodTest(unittest.TestCase):

  def setUp(self):
    self.session = whole_font_pfe_method.start_session(
        font_loader.FontLoader("./patch_subset/testdata/"))

  def test_font_not_found(self):
    with self.assertRaises(IOError):
      self.session.page_view({"Roboto-Bold.ttf": [0x61, 0x62]})

  def test_single_file_load(self):
    self.session.page_view({"Roboto-Regular.ttf": [0x61, 0x62]})

    graphs = self.session.get_request_graphs()
    self.assertEqual(len(graphs), 1)
    self.assertTrue(
        request_graph.graph_has_independent_requests(graphs[0], [
            (0, ROBOTO_REGULAR_WOFF2_SIZE),
        ]))

  def test_cached_file_load(self):
    session = whole_font_pfe_method.start_session(
        font_loader.FontLoader("./patch_subset/testdata/"))
    session.page_view({"Roboto-Regular.ttf": [0x61, 0x62]})
    session = whole_font_pfe_method.start_session(
        font_loader.FontLoader("./patch_subset/testdata/"))
    session.page_view({"Roboto-Regular.ttf": [0x63, 0x64]})

    graphs = session.get_request_graphs()
    self.assertEqual(len(graphs), 1)
    self.assertTrue(
        request_graph.graph_has_independent_requests(graphs[0], [
            (0, ROBOTO_REGULAR_WOFF2_SIZE),
        ]))

  def test_multiple_file_load(self):
    self.session.page_view({"Roboto-Regular.ttf": [0x61, 0x62]})
    self.session.page_view({"Roboto-Thin.ttf": [0x61, 0x62]})

    graphs = self.session.get_request_graphs()
    self.assertEqual(len(graphs), 2)
    self.assertTrue(
        request_graph.graph_has_independent_requests(graphs[0], [
            (0, ROBOTO_REGULAR_WOFF2_SIZE),
        ]))
    self.assertTrue(
        request_graph.graph_has_independent_requests(graphs[1], [
            (0, ROBOTO_THIN_WOFF2_SIZE),
        ]))

  def test_parallel_file_loads(self):
    self.session.page_view({
        "Roboto-Regular.ttf": [0x61, 0x62],
        "Roboto-Thin.ttf": [0x61, 0x62],
    })

    graphs = self.session.get_request_graphs()
    self.assertEqual(len(graphs), 1)
    self.assertTrue(
        request_graph.graph_has_independent_requests(graphs[0], [
            (0, ROBOTO_REGULAR_WOFF2_SIZE),
            (0, ROBOTO_THIN_WOFF2_SIZE),
        ]))

  def test_single_file_loads_only_once(self):
    self.session.page_view({"Roboto-Regular.ttf": [0x61, 0x62]})
    self.session.page_view({"Roboto-Regular.ttf": [0x63, 0x64]})

    graphs = self.session.get_request_graphs()
    self.assertEqual(len(graphs), 2)
    self.assertTrue(
        request_graph.graph_has_independent_requests(graphs[0], [
            (0, ROBOTO_REGULAR_WOFF2_SIZE),
        ]))
    self.assertTrue(request_graph.graph_has_independent_requests(graphs[1], []))

  def test_ignores_no_codepoint_font(self):
    self.session.page_view({"Roboto-Regular.ttf": []})

    graphs = self.session.get_request_graphs()
    self.assertEqual(len(graphs), 1)
    self.assertTrue(request_graph.graph_has_independent_requests(graphs[0], []))


if __name__ == '__main__':
  unittest.main()
