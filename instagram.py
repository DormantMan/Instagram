#! /usr/bin/env python
# -*- coding: utf-8 -*-

#
#      Instagram
#
#    This version: 0.1.0a
#
#       Author: DormantMan
#

import time

from InstagramAPI import InstagramAPI


class Instagram:
    version = '0.1.0a'

    def __init__(self, time_flip_posts=0.75, time_wait_unlock=1800):
        print('Instagram %s' % self.version)
        self.api = InstagramAPI('', '')

        self.time_flip_posts = time_flip_posts
        self.time_wait_unlock = time_wait_unlock

    def get_status(self):
        return self.api.isLoggedIn

    def auth(self, username, password):
        self.api = InstagramAPI(username, password)
        self.api.login(force=True)
        return self.api.isLoggedIn

    def find_user(self, username):
        if self.api.fbUserSearch(username):
            if self.api.LastJson['users']:
                return self.api.LastJson['users'][0]['user']['pk'], username

    def like_feed_user(self, username=None, max_likes=-1, user_id=None):
        if not user_id:
            if username:
                user_id, username = self.find_user(username)
            else:
                return print('User with such a nickname does not exist.')

        if self.api.getUserFeed(user_id):
            media_count = 0
            sum_likes = 0
            now_count = 0
            max_id = ''
            total = 0

            print(f'Starting liking {username}\'s media...')

            while True:
                if max_id == 'end':
                    return print(f'Mission complete :)\n'
                                 f'[Posts ended]\n'
                                 f'Result: {total}/{media_count} ({round(total/media_count*100, 2)}%)\n'
                                 f'The average of likes: {round(sum_likes/media_count, 2)}')

                self.api.getUserFeed(user_id, maxid=max_id)
                media = self.api.LastJson

                max_id = 'end' if 'next_max_id' not in media else media['next_max_id']

                media = media['items']
                media_count += len(media)

                self.log(f'Total media count: {media_count}')

                for post in media:
                    if now_count >= max_likes >= 0:
                        return print(f'Mission complete :)\n'
                                     f'[The maximum is reached]\n'
                                     f'Result: {total}/{now_count} ({round(total/now_count*100, 2)}%)\n'
                                     f'The average of likes: {round(sum_likes/now_count, 2)}')
                    now_count += 1

                    media_id = post['pk']
                    likes = post['like_count']
                    pinpoint = time.process_time()

                    sum_likes += likes

                    if post['has_liked']:
                        self.log(f'\r{now_count}\t-\tMedia {media_id} [likes:{likes}]\t[old like] *')

                    else:
                        while True:
                            try:
                                if self.api.like(media_id):
                                    total += 1
                                    self.log(f'\r{now_count}\t-\tMedia {media_id} [likes:{likes}]\t[new like] +')
                                    time.sleep(min(pinpoint - self.time_flip_posts, 0))
                                break

                            except (Exception, BaseException):
                                print('\nAccount temporarily blocked')
                                print('Time to wait for unlock: {}'.format(self.time_wait_unlock))

                                pinpoint = time.process_time()
                                while (time.process_time() - pinpoint) < self.time_wait_unlock:
                                    self.log('\rTime left: {} s'.format(round(time.process_time() - pinpoint)))

                                print('Try again...')

                self.log(f'Liked {total}/{media_count} media')
        else:
            print('Unable to get user\'s feed.')

    @staticmethod
    def log(s):
        print(s)
        # sys.stdout.flush()

    def logout(self):
        self.api.logout()


if __name__ == '__main__':
    client = Instagram(time_flip_posts=1.25, time_wait_unlock=1800)
    client.auth('username', 'password')
    s_username = input('Input username: ')
    s_user_id, s_username = client.find_user(s_username)
    print('Nick - {} [{}]'.format(s_username, s_user_id))
    client.like_feed_user(s_username, -1)
