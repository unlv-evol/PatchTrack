import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from analyzer import analysis


def test_all_class_bar_no_plotting():
    # should run without raising
    analysis.all_class_bar([1, 2, 3, 4, 5], pr_nr=1, plotting=False)


def test_all_class_bar_with_plotting(monkeypatch):
    called = {'show': False}

    def fake_show():
        called['show'] = True

    monkeypatch.setattr(plt, 'show', fake_show)
    analysis.all_class_bar([1, 2, 3, 4, 5], pr_nr=2, plotting=True)
    assert called['show'] is True


def test_create_pie_and_bar_on_axes():
    fig, ax = plt.subplots()
    analysis.create_pie([10, 20, 30, 25, 15], ax)
    analysis.create_bar([10, 20, 30, 25, 15], ax)
    plt.close(fig)


def test_grouped_bar_chart_saves(monkeypatch):
    saved = {'fname': None}

    def fake_save(fname, **kwargs):
        saved['fname'] = fname

    monkeypatch.setattr(plt, 'savefig', fake_save)
    monkeypatch.setattr(plt, 'show', lambda: None)

    # grouped_bar_chart expects lists whose length defines positions; use length 10
    y = [1] * 10
    # provide six lists of equal length
    analysis.grouped_bar_chart(y, y, y, y, y, y, repo_nr=42)
    assert saved['fname'] is not None
    assert 'Grouped_bar_42' in saved['fname']


def test_create_all_bars_and_pies_save(monkeypatch, tmp_path):
    saved = []

    def fake_save(fname, **kwargs):
        saved.append(fname)

    monkeypatch.setattr(plt, 'savefig', fake_save)
    monkeypatch.setattr(plt, 'show', lambda: None)

    # monkeypatch create_bar/create_pie to avoid passing `plt` as an Axes
    def fake_create_bar(height, ax):
        saved.append(f"bar:{len(height)}")

    def fake_create_pie(slices, ax):
        saved.append(f"pie:{len(slices)}")

    monkeypatch.setattr(analysis, 'create_bar', fake_create_bar)
    monkeypatch.setattr(analysis, 'create_pie', fake_create_pie)

    # create data for 10 intervals
    data = {str(i): [1, 2, 3, 4, 5] for i in range(10)}
    analysis.create_all_bars(data, repo_nr=7)
    analysis.create_all_pie(data, repo_nr=7)
    assert any('bar:' in s or 'pie:' in s for s in saved)


def test_all_class_bar_w_even_d_saves(monkeypatch):
    saved = {'fname': None}

    def fake_save(fname, **kwargs):
        saved['fname'] = fname

    monkeypatch.setattr(plt, 'savefig', fake_save)

    height = [1, 2, 3, 4, 5, 6, 7, 8]
    analysis.all_class_bar_w_even_d(height, pr_nr=99)
    assert saved['fname'] is not None
    assert 'All_Classes_Bar_70_EVED_99' in saved['fname']


def test_all_class_pie_plotting_flag(monkeypatch):
    shown = {'val': False}

    def fake_show():
        shown['val'] = True

    monkeypatch.setattr(plt, 'show', fake_show)
    analysis.all_class_pie([10, 20, 30, 40, 0], pr_nr=3, plotting=True)
    assert shown['val'] is True
