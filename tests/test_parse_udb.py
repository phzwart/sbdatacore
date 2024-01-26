import pytest
import os
from sbdatacore.parse_udb import get_user_bd, inverse_search

@pytest.fixture
def create_temp_user_db():
    # Setup - creating a temporary file with test data
    temp_filename = "temp_user_db.txt"
    with open(temp_filename, "w") as file:
        file.write("#NERSC FACILITY\n")
        file.write("kharris kamala\n")
        file.write("mpence mike\n")
        file.write("mpence mikey\n")
    yield temp_filename
    # Teardown - deleting the temporary file
    os.remove(temp_filename)

def test_get_user_bd(create_temp_user_db):
    # Test
    result = get_user_bd(create_temp_user_db)
    assert result == {
        "kharris": ["kamala"],
        "mpence": ["mike", "mikey"]
    }

def test_inverse_search():
    user_bd = {
        "kharris": ["kamala"],
        "mpence": ["mike", "mikey"]
    }
    assert inverse_search(user_bd, "kamala") == "kharris"
    assert inverse_search(user_bd, "mikey") == "mpence"

    # Test for item not found
    with pytest.raises(ValueError) as excinfo:
        inverse_search(user_bd, "unknown")
    assert "not found" in str(excinfo.value)

    # Test for non-unique item
    user_bd["other_user"] = ["kamala"]
    with pytest.raises(ValueError) as excinfo:
        inverse_search(user_bd, "kamala")
    assert "not uniquely associated" in str(excinfo.value)

# Run tests if the script is executed directly
if __name__ == "__main__":
    pytest.main()

