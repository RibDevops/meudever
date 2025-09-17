#import necessary module
# class GroupViewSet(viewset.ModelViewSet):
#     """
#     Model View Set for Group
#     """

#     serializer_class = GroupSerializer
#     queryset = Group.objects.all()
#     pagination_class = None
#     permission_classes = [IsAuthenticated, IsAdminUser]
#     lookup_field = "pk"
#     http_method_names = ("get", "post", "patch", "delete")

#     def list(self, request, *args, **kwargs):
#         return super().list(request, fields=("id", "name"), *args, **kwargs)