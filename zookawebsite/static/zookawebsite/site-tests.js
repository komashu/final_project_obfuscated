var passed_msg = "Passed!";
QUnit.test("sanity test", function(assert) {
    assert.ok(1 == "1", passed_msg);
});
QUnit.test("getCookie() test", function(assert) {
    assert.ok(null != getCookie('csrftoken'), passed_msg);
});
