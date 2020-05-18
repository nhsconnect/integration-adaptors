projects=("$@")

if [ -z "$projects" ]
then
    projects=( "common" "mhs/common" "mhs/outbound" "mhs/inbound" "mhs/spineroutelookup" "integration-tests/integration_tests" "SCR" "SCRWebService" )
fi

for i in "${projects[@]}"
do
    echo "-----------------------------"
    echo "--- Installing virtualenv in '$i'"
    echo "-----------------------------"
    (cd $i; pipenv --rm; pipenv install --dev --clear; pipenv update --clear)
done
