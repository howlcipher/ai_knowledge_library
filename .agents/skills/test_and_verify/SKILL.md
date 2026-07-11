name: "test_and_verify"
description: "Triggers during feature validations, build cycles, or local environment checks"

# Validation Framework

* Discover the current directory structure to find the native testing tools present.
* Execute the validation framework automatically following any substantial code modification.
* Never classify a workspace task as successful if the build runner outputs a failure exit status.\n