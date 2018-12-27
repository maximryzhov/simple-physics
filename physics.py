import sys
from math import copysign, inf

import pygame

from vectors import Vector2D


# from https://stackoverflow.com/a/20677983
def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return None

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return Vector2D(x, y)


class RigidBody:
    def __init__(self, width, height, x, y, angle=0.0, mass=None, restitution=0.5):
        self.position = Vector2D(x, y)
        self.width = width
        self.height = height
        self.angle = angle

        self.velocity = Vector2D(0.0, 0.0)
        self.angular_velocity = 0.0

        self.torque = 0.0
        self.forces = Vector2D(0.0, 0.0)
        if mass is None:
            mass = width * height
        self.mass = mass
        self.restitution = restitution
        self.inertia = mass * (width ** 2 + height ** 2) / 12

        self.sprite = pygame.Surface((width, height))
        self.sprite.set_colorkey((0, 0, 0))
        self.sprite.fill((0, 0, 0))
        pygame.draw.rect(self.sprite, (255, 255, 255), (0, 0, width - 2, height - 2), 2)

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.sprite, self.angle)
        rect = rotated.get_rect()
        surface.blit(rotated, self.position - (rect.width / 2, rect.height / 2))

    def add_world_force(self, force, offset):

        if abs(offset[0]) <= self.width / 2 and abs(offset[1]) <= self.height / 2:
            self.forces += force
            self.torque += offset.cross(force.rotate(self.angle))

    def add_torque(self, torque):
        self.torque += torque

    def reset(self):
        self.forces = Vector2D(0.0, 0.0)
        self.torque = 0.0

    def update(self, dt):
        acceleration = self.forces / self.mass
        self.velocity += acceleration * dt
        self.position += self.velocity * dt

        angular_acceleration = self.torque / self.inertia
        self.angular_velocity += angular_acceleration * dt
        self.angle += self.angular_velocity * dt

        self.reset()

    @property
    def vertices(self):
        return [
            self.position + Vector2D(v).rotate(-self.angle) for v in (
                (-self.width / 2, -self.height / 2),
                (self.width / 2, -self.height / 2),
                (self.width / 2, self.height / 2),
                (-self.width / 2, self.height / 2)
            )
        ]

    @property
    def edges(self):
        return [
            Vector2D(v).rotate(self.angle) for v in (
                (self.width, 0),
                (0, self.height),
                (-self.width, 0),
                (0, -self.height),
            )
        ]

    def collide(self, other):
        # Exit early for optimization
        if (self.position - other.position).length() > max(self.width, self.height) + max(other.width, other.height):
            return False, None, None

        def project(vertices, axis):
            dots = [vertex.dot(axis) for vertex in vertices]
            return Vector2D(min(dots), max(dots))

        collision_depth = sys.maxsize
        collision_normal = None

        for edge in self.edges + other.edges:
            axis = Vector2D(edge).orthogonal().normalize()
            projection_1 = project(self.vertices, axis)
            projection_2 = project(other.vertices, axis)
            min_intersection = max(min(projection_1), min(projection_2))
            max_intersection = min(max(projection_1), max(projection_2))
            overlapping = min_intersection <= max_intersection
            if not overlapping:
                return False, None, None
            else:
                overlap = max_intersection - min_intersection
                if overlap < collision_depth:
                    collision_depth = overlap
                    collision_normal = axis
        return True, collision_depth, collision_normal

    def get_collision_edge(self, normal):
        max_projection = -sys.maxsize
        support_point = None
        vertices = self.vertices
        length = len(vertices)

        for i, vertex in enumerate(vertices):
            projection = vertex.dot(normal)
            if projection > max_projection:
                max_projection = projection
                support_point = vertex
                if i == 0:
                    right_vertex = vertices[-1]
                else:
                    right_vertex = vertices[i - 1]
                if i == length - 1:
                    left_vertex = vertices[0]
                else:
                    left_vertex = vertices[i + 1]

        if right_vertex.dot(normal) > left_vertex.dot(normal):
            return (right_vertex, support_point)
        else:
            return (support_point, left_vertex)


class PhysicsWorld:
    def __init__(self):
        self.bodies = []

    def add(self, *bodies):
        self.bodies += bodies
        for body in bodies:
            print("Body added", id(body))

    def remove(self, body):
        self.bodies.remove(body)
        print("Body removed", id(body))

    def update(self, dt):
        tested = []
        for body in self.bodies:

            for other_body in self.bodies:
                if other_body not in tested and other_body is not body:
                    collision, depth, normal = body.collide(other_body)

                    if collision:
                        normal = normal.normalize()

                        rel_vel = (body.velocity - other_body.velocity)
                        j = -(1 + body.restitution) * rel_vel.dot(normal) / normal.dot(
                            normal * (1 / body.mass + 1 / other_body.mass))

                        direction = body.position - other_body.position
                        magnitude = normal.dot(direction)

                        if body.mass != inf:
                            body.position += normal * depth * copysign(1, magnitude)
                        if other_body.mass != inf:
                            other_body.position -= normal * depth * copysign(1, magnitude)

                        body.velocity = body.velocity + j / body.mass * normal
                        other_body.velocity = other_body.velocity - j / other_body.mass * normal

                        body_collision_edge = body.get_collision_edge(-direction)
                        other_body_collision_edge = other_body.get_collision_edge(direction)
                        contact_point = line_intersection(body_collision_edge, other_body_collision_edge)

                        if contact_point:
                            radius = (body.position - contact_point)
                            body.angular_velocity = body.angular_velocity + (radius.dot(j * normal / body.inertia))

                            radius = (other_body.position - contact_point)
                            other_body.angular_velocity = other_body.angular_velocity - (
                                radius.dot(j * normal / other_body.inertia))

            tested.append(body)
            body.update(dt)
