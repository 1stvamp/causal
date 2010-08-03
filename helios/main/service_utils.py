def get_model_instance(user, module_name):
    return UserService.objects.get(user=user, app__module_name=module_name)