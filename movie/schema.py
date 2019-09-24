import graphene
import graphql_jwt
from graphene_django.types import DjangoObjectType
from .models import Movies, Director


# TYPES
class MovieType(DjangoObjectType):
    class Meta:
        model = Movies

    movie_age = graphene.String()

    def resolve_movie_age(self, info):
        if self.year < 1995:
            return "Old Movie"
        else:
            return "New Movie"

class DirectorType(DjangoObjectType):
    class Meta:
        model = Director


# QUERIES
class Query(graphene.ObjectType):
    all_movies = graphene.List(MovieType)
    movie = graphene.Field(MovieType, id=graphene.Int(), title=graphene.String())
    all_directors = graphene.List(DirectorType)

    def resolve_all_movies(self, info, **kwargs):
        user = info.context.user
        return user.is_authenticated
        # if is no user.is_authenticated:
        #     return Movies.objects.all()

    def resolve_movie(self, info, **kwargs):
        id = kwargs.get("id")
        title = kwargs.get("title")

        if id is not None:
            return Movies.objects.get(pk=id)

        if title is not None:
            return Movies.objects.get(title=title)
        
        return None

    def resolve_all_directors(self, info):
        return Director.objects.all()

class MovieCreateMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        year = graphene.Int(required=True)

    movie = graphene.Field(MovieType)

    def mutate(self, info, title, year):
        movie = Movies.objects.create(title=title, year=year)

        return MovieCreateMutation(movie=movie)

class UpdateMovieMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        year = graphene.Int()
        id = graphene.ID(required=True)

    movie = graphene.Field(MovieType)

    def mutate(self, info, id, title, year):
        movie = Movies.objects.get(pk=id)
        
        if title is not None:
            movie.title = title

        if year is not None:
            movie.year = year

        movie.save()

        return UpdateMovieMutation(movie=movie)

class DeleteMovieMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    movie = graphene.Field(MovieType)

    def mutate(self, info, id):
        movie = Movies.objects.get(pk=id)
        movie.delete()

        return DeleteMovieMutation(movie=movie)


class Mutation:
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    create_movie = MovieCreateMutation.Field()
    update_movie = UpdateMovieMutation.Field()
    delete_movie = DeleteMovieMutation.Field()