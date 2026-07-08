from app.crud.analytics import build_summary, build_analytics, build_reports


class TestBuildSummary:
    def test_empty_expenses(self):
        summary = build_summary([])
        assert summary["count"] == 0
        assert summary["total"] == 0.0
        assert summary["total_income"] == 0.0
        assert summary["balance"] == 0.0
        assert summary["categories"] == []
        assert summary["top_category"] == "None yet"

    def test_with_expenses_only(self, sample_expenses):
        summary = build_summary(sample_expenses)
        total = 150.0 + 80.0 + 45.0 + 15.99 + 50.0
        assert summary["count"] == 5
        assert summary["total"] == total
        assert summary["total_income"] == 0.0
        assert summary["balance"] == -total
        assert len(summary["categories"]) == 4

    def test_with_expenses_and_income(self, sample_expenses, sample_income):
        summary = build_summary(sample_expenses, income=sample_income)
        total_spent = 150.0 + 80.0 + 45.0 + 15.99 + 50.0
        total_income = 5000.0 + 500.0
        assert summary["total"] == total_spent
        assert summary["total_income"] == total_income
        assert summary["balance"] == total_income - total_spent

    def test_top_category(self, sample_expenses):
        summary = build_summary(sample_expenses)
        assert summary["top_category"] == "Food"
        assert summary["categories"][0][0] == "Food"

    def test_category_progress(self, sample_expenses, sample_categories):
        summary = build_summary(sample_expenses, categories=sample_categories)
        assert len(summary["category_progress"]) == 4
        food_progress = next(c for c in summary["category_progress"] if c["name"] == "Food")
        assert food_progress["spent"] == 195.0
        assert food_progress["limit"] == 500.0
        assert food_progress["is_over"] is False

    def test_budget_overage(self, sample_expenses, sample_categories):
        large_expenses = sample_expenses + [
            {"title": "New TV", "amount": 2000.0, "category": "Entertainment",
             "expense_date": "2026-07-03", "notes": ""}
        ]
        summary = build_summary(large_expenses, categories=sample_categories)
        ent_progress = next(c for c in summary["category_progress"] if c["name"] == "Entertainment")
        assert ent_progress["is_over"] is True
        assert ent_progress["percentage"] == 100.0

    def test_chart_data_structure(self, sample_expenses):
        summary = build_summary(sample_expenses)
        assert set(summary["chart_data"].keys()) == {
            "labels", "values", "category_labels", "category_values", "category_colors"
        }
        assert len(summary["chart_data"]["category_labels"]) == 4
        assert len(summary["chart_data"]["category_values"]) == 4

    def test_daily_trend(self, sample_expenses):
        summary = build_summary(sample_expenses)
        trend_labels = summary["chart_data"]["labels"]
        trend_values = summary["chart_data"]["values"]
        assert len(trend_labels) == len(trend_values) > 0
        assert trend_labels == sorted(set(e["expense_date"] for e in sample_expenses))


class TestBuildAnalytics:
    def test_empty(self):
        summary = build_summary([])
        analytics = build_analytics([], summary)
        assert analytics["categories"] == []
        assert analytics["insights"] == []

    def test_category_breakdown(self, sample_expenses):
        summary = build_summary(sample_expenses)
        analytics = build_analytics(sample_expenses, summary)
        assert len(analytics["categories"]) == 4
        food = next(c for c in analytics["categories"] if c["category"] == "Food")
        assert food["amount"] == 195.0
        assert 0 < food["percentage"] <= 100

    def test_insights_generated(self, sample_expenses):
        summary = build_summary(sample_expenses)
        analytics = build_analytics(sample_expenses, summary)
        assert len(analytics["insights"]) > 0
        assert "Food" in analytics["insights"][0]

    def test_insights_high_spend_warning(self, sample_expenses):
        skewed = sample_expenses + [
            {"title": "Rent", "amount": 3000.0, "category": "Housing",
             "expense_date": "2026-07-01", "notes": ""},
        ]
        summary = build_summary(skewed)
        analytics = build_analytics(skewed, summary)
        assert any("significantly higher" in i for i in analytics["insights"])


class TestBuildReports:
    def test_empty(self):
        assert build_reports([]) == []

    def test_monthly_grouping(self, sample_expenses):
        reports = build_reports(sample_expenses)
        assert len(reports) > 0
        for report in reports:
            assert "month" in report
            assert "spent" in report
            assert "income" in report
            assert "balance" in report

    def test_income_in_reports(self, sample_expenses, sample_income):
        reports = build_reports(sample_expenses, sample_income)
        july = next(r for r in reports if r["month"] == "2026-07")
        assert july["income"] == 5500.0
        assert july["balance"] == july["income"] - july["spent"]

    def test_reports_sorted_descending(self, sample_expenses):
        reports = build_reports(sample_expenses)
        months = [r["month"] for r in reports]
        assert months == sorted(months, reverse=True)
