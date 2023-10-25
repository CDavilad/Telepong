all: compile link

compile:
	gcc PaddleSync.c server.c -o server -lpthread

link:
	./server 8888 logger.txt

clean:
	rm -f serverThreads 