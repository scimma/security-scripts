aws iam attach-role-policy --role-name scimma_test_power_user --policy-arn arn:aws:iam::585193511743:policy/ProposedPoweruser
aws iam detach-role-policy --role-name scimma_test_power_user --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
