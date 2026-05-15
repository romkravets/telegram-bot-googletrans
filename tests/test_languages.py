from languages import search_language, LANGUAGES, TOP_10_CODES

def test_search_exact_english_name():
    result = search_language("Polish")
    assert result == "pl"

def test_search_case_insensitive():
    result = search_language("polish")
    assert result == "pl"

def test_search_partial_match():
    result = search_language("Germ")
    assert result == "de"

def test_search_by_code():
    result = search_language("uk")
    assert result == "uk"

def test_search_unknown_language():
    result = search_language("Klingon")
    assert result is None

def test_top10_codes_are_valid():
    for code in TOP_10_CODES:
        assert code in LANGUAGES

def test_language_has_required_fields():
    for code, info in LANGUAGES.items():
        assert "name" in info, f"{code} missing 'name'"
        assert "flag" in info, f"{code} missing 'flag'"
        assert "deepl" in info, f"{code} missing 'deepl'"
        assert "google" in info, f"{code} missing 'google'"
