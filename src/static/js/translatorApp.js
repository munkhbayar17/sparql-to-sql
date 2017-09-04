var myApp = angular.module('transApp', [])

myApp.controller('translatorApp', function ($scope, $http) {

    $scope.sparql = "SELECT ?a ?f ?l ?g WHERE {?a person:lastname ?l . ?a person:age ?g . ?a person:firstname ?f}";
    $scope.validSql = false;
    $scope.messageClass = "message-success";
    $scope.anyResult = false;
    $scope.sqlResult = [];
    $scope.dbName = "Persons";
    $scope.translatorType = "1";
    $scope.sortType = "s";
    $scope.sortReverse = true;
    $scope.translating = false;
    $scope.recordCount = 0;

    var last_run_db_name = "Persons";

    $scope.translate = function () {

        if ($scope.sparql) {

            $scope.showResult = false;
            $scope.sqlResult = [];
            $scope.translating = true;

            $http({
                url: '/trans',
                method: "POST",
                data: {
                    sparql: $scope.sparql,
                    translatorType: $scope.translatorType
                }
            })
                .then(function (response) {
                        $scope.sql = response.data.sql;
                        $scope.sqlQuery = response.data.sql;

                        if(response.data.is_valid)
                            $scope.validSql = response.data.is_valid;

                        if ($scope.validSql) {
                            $scope.messageClass = "message-success";
                            $scope.messageText = "SQL query is valid";
                        }
                        else {
                            $scope.messageClass = "message-error";
                            $scope.messageText = "SQL query is not valid";
                        }

                        if (response.data.header) {
                            $scope.headers = response.data.header;
                        }

                        if (response.data.result && response.data.result.length > 0) {
                            $scope.sqlResult = response.data.result;
                            $scope.resultMsg = response.data.result.length + " records.";
                            $scope.anyResult = true;
                        }
                        else {
                            $scope.resultMsg = "no record found."
                            $scope.anyResult = false;
                        }
                        $scope.translating = false;
                    },
                    function (response) {
                        $scope.messageClass = "message-error";
                        $scope.messageText = "Translation failed!"
                        $scope.translating = false;
                    });
        }
    }

    $scope.runQuery = function () {
        $scope.showResult = true;

        //if($scope.sqlQuery != $scope.sql || $scope.dbName != last_run_db_name) {
            last_run_db_name = $scope.dbName;

            $http({
                url: '/run',
                method: "POST",
                data: $scope.sql
            })
                .then(function (response) {

                        $scope.validSql = response.data.is_valid;

                        if ($scope.validSql) {
                            $scope.messageClass = "message-success";
                            $scope.messageText = "SQL query is valid";
                        }
                        else {
                            $scope.messageClass = "message-error";
                            $scope.messageText = "SQL query is not valid";
                        }


                        if (response.data.result && response.data.result.length > 0) {
                            $scope.sqlResult = response.data.result;
                            $scope.resultMsg = response.data.result.length + " records.";
                            $scope.anyResult = true;
                        }
                        else {
                            $scope.resultMsg = "no record found.";
                            $scope.anyResult = false;
                        }
                    },
                    function (response) {
                        $scope.messageClass = "message-error";
                        $scope.messageText = "SQL run failed!"
                    });
        //}
    }

    $scope.change_db = function() {
        if($scope.dbName) {
            $scope.sqlResult = [];

            $http({
                url: '/changedb',
                method: "POST",
                data: $scope.dbName
            })
                .then(function (response) {
                        $scope.messageClass = "message-success";
                        $scope.messageText = "Dataset has been changed"
                    },
                    function (response) {
                        $scope.messageClass = "message-error";
                        $scope.messageText = "Dataset could not be change!"
                    });
        }
    }
});