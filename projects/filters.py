from rest_framework.filters import BaseFilterBackend


class ProjectFileByProjectFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        project_id = request.query_params.get('project')
        if project_id:
            return queryset.filter(project_id=project_id)
        return queryset
