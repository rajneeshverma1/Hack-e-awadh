# Data Serializers for OrgLens API
from rest_framework import serializers
from .models import Repository, Issue, Commit, RepositoryWork, Contributor

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'

class CommitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commit
        fields = '__all__'

class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = '__all__'

class RepositoryWorkSerializer(serializers.ModelSerializer):
    issues = IssueSerializer(many=True, read_only=True)
    commits = CommitSerializer(many=True, read_only=True)

    class Meta:
        model = RepositoryWork
        fields = '__all__'

class ContributorSerializer(serializers.ModelSerializer):
    works = RepositoryWorkSerializer(many=True, read_only=True)

    class Meta:
        model = Contributor
        fields = '__all__'

class DataSerializer(serializers.Serializer):
    repositories = RepositorySerializer(many=True, read_only=True)
    contributors = ContributorSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        """
        Optimized representation fetching with prefetch_related to eliminate N+1 queries.
        """
        contributors_qs = Contributor.objects.all().prefetch_related(
            'works__issues',
            'works__commits'
        )
        return {
            'repositories': RepositorySerializer(Repository.objects.all(), many=True).data,
            'contributors': ContributorSerializer(contributors_qs, many=True).data
        }

    # If this serializer is meant to serialize a specific object that holds
    # references to all repositories and contributors, the implementation
    # would need to change based on that object's structure.
    # For now, it assumes it will be instantiated without an instance and
    # will fetch all data directly.