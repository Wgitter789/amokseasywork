#include <iostream>
#include <string>
#include <fstream>
#include <cstring>
#include <limits>
#include <cstdlib>
#include <algorithm>

using namespace std;

#define MAXV 40
#define MAXE 200
#define INF 999999
// 顶点结构
struct Vertex
{
    int id;
    string name;
	string description;
	int timeOfVisit=0;
};

// 边结点
struct Edge
{
    int to;
    int weight;

    Edge* next;
};
// 全局变量
bool vis[MAXV];

// 顶点表
Vertex vertex[MAXV];

// 邻接矩阵
int adjMatrix[MAXV][MAXV];

// 邻接表头指针
Edge* head[MAXV];

// 边结点池
Edge edgePool[MAXE];

// 当前边数
int edgeCnt = 0;

// 顶点数
int vertexCount = 0;

// 边数
int edgeCount = 0;

// 初始化邻接矩阵
void initMatrix()
{
    for (int i = 0; i < MAXV; i++)
    {
        for (int j = 0; j < MAXV; j++)
        {
            if (i == j)
                adjMatrix[i][j] = 0;
            else
                adjMatrix[i][j] = INF;
        }
    }
}
// 添加一条边到邻接表

void addEdge(int u, int v, int w)
{
    edgePool[edgeCnt].to = v;
    edgePool[edgeCnt].weight = w;

    edgePool[edgeCnt].next = head[u];

    head[u] = &edgePool[edgeCnt];

    edgeCnt++;
}
// 插入无向边
void insertRoad(int u, int v, int w)
{
    adjMatrix[u][v] = w;
    adjMatrix[v][u] = w;

    addEdge(u, v, w);
    addEdge(v, u, w);
}

// 从TXT文件读取地图
void loadMap(const char* filename)
{
    ifstream fin(filename);

    if (!fin)
    {
        cout << "地图数据文件打开失败！" << endl;
        return;
    }

    // 顶点数
    fin >> vertexCount;

    // 边数
    fin >> edgeCount;

    // 读取顶点
    for (int i = 1; i <= vertexCount; i++)
    {
        fin >> vertex[i].id >> vertex[i].name >> vertex[i].description;
    }

    // 读取边
    int u, v, w;

    for (int i = 0; i < edgeCount; i++)
    {
        fin >> u >> v >> w;

        insertRoad(u, v, w);
    }

    fin.close();

    cout << "地图数据加载成功！" << endl;
}
// 输出景点信息
void printVertex()
{
    cout << "\n========== 景点列表 ==========\n";

    for (int i = 1; i <= vertexCount; i++)
    {
        cout
            << vertex[i].id
            << " "
            << vertex[i].name
            << endl;
    }
}

// 输出邻接表
void printAdjList()
{
    cout << "\n========== 邻接表 ==========\n";

    for (int i = 1; i <= vertexCount; i++)
    {
        cout << vertex[i].name << " : ";

        Edge* p = head[i];

        while (p != NULL)
        {
            cout
                << "("
                << vertex[p->to].name
                << ","
                << p->weight
                << ") ";

            p = p->next;
        }

        cout << endl;
    }
}
// 输出邻接矩阵
void printAdjMatrix()
{
    cout << "\n========== 邻接矩阵 ==========\n";

    cout << "\t";

    for (int i = 1; i <= vertexCount; i++)
    {
        cout << i << "\t";
    }

    cout << endl;

    for (int i = 1; i <= vertexCount; i++)
    {
        cout << i << "\t";

        for (int j = 1; j <= vertexCount; j++)
        {
            if (adjMatrix[i][j] == INF)
                cout << "∞\t";
            else
                cout << adjMatrix[i][j] << "\t";
        }

        cout << endl;
    }
}
// Floyd最短路径矩阵
int distFloyd[MAXV][MAXV];

// Floyd路径恢复矩阵
int nextFloyd[MAXV][MAXV];
int dist[MAXV];
int pre[MAXV];
void initFloyd()
{
    for (int i = 1; i <= vertexCount; i++)
    {
        for (int j = 1; j <= vertexCount; j++)
        {
            distFloyd[i][j] = adjMatrix[i][j];

            if (i != j && adjMatrix[i][j] != INF)
                nextFloyd[i][j] = j;
            else
                nextFloyd[i][j] = -1;
        }
    }
}
void floyd()
{
    for (int k = 1; k <= vertexCount; k++)
    {
        for (int i = 1; i <= vertexCount; i++)
        {
            for (int j = 1; j <= vertexCount; j++)
            {
                if (distFloyd[i][k] == INF)
                    continue;

                if (distFloyd[k][j] == INF)
                    continue;

                if (distFloyd[i][j] >
                    distFloyd[i][k] + distFloyd[k][j])
                {
                    distFloyd[i][j] =
                        distFloyd[i][k] + distFloyd[k][j];

                    nextFloyd[i][j] =
                        nextFloyd[i][k];
                }
            }
        }
    }
}
void printFloydMatrix()
{
    cout << "\n===== Floyd最短路径矩阵 =====\n";

    for (int i = 1; i <= vertexCount; i++)
    {
        for (int j = 1; j <= vertexCount; j++)
        {
            if (distFloyd[i][j] == INF)
                cout << "INF\t";
            else
                cout << distFloyd[i][j] << "\t";
        }

        cout << endl;
    }
}
void printFloydPath(int start, int end)
{
    if (nextFloyd[start][end] == -1)
    {
        cout << "不存在路径" << endl;
        return;
    }

    cout << vertex[start].name;

    int cur = start;

    while (cur != end)
    {
        cur = nextFloyd[cur][end];

        cout << " -> " << vertex[cur].name;
    }

    cout << endl;
}
void shortestPath(int start, int end)
{
    if (distFloyd[start][end] == INF)
    {
        cout << "两点不可达！" << endl;
        return;
    }

    cout << "\n最短距离："
        << distFloyd[start][end]
        << endl;

    cout << "最短路径：";

    printFloydPath(start, end);
}
void dijkstra(int start)
{
    for (int i = 1; i <= vertexCount; i++)
    {
        dist[i] = INF;
        pre[i] = -1;
        vis[i] = false;
    }

    dist[start] = 0;

    for (int i = 1; i <= vertexCount; i++)
    {
        int u = -1;
        int MIN = INF;

        for (int j = 1; j <= vertexCount; j++)
        {
            if (!vis[j] && dist[j] < MIN)
            {
                MIN = dist[j];
                u = j;
            }
        }

        if (u == -1)
            break;

        vis[u] = true;

        Edge* p = head[u];

        while (p)
        {
            int v = p->to;

            if (!vis[v] &&
                dist[v] > dist[u] + p->weight)
            {
                dist[v] =
                    dist[u] + p->weight;

                pre[v] = u;
            }

            p = p->next;
        }
    }
}
void printDijkstraPath(int start, int end)
{
    if (start == end)
    {
        cout << vertex[start].name;
        return;
    }

    if (pre[end] == -1)
    {
        cout << "无路径";
        return;
    }

    printDijkstraPath(start, pre[end]);

    cout << " -> " << vertex[end].name;
}
void printDijkstraResult(int start)
{
    cout << "\n===== 单源最短路径 =====\n";

    for (int i = 1; i <= vertexCount; i++)
    {
        if (i == start)
            continue;

        cout << "\n目的地："
            << vertex[i].name
            << endl;

        if (dist[i] == INF)
        {
            cout << "不可达" << endl;
            continue;
        }

        cout << "距离："
            << dist[i]
            << endl;

        cout << "路径：";

        printDijkstraPath(start, i);

        cout << endl;
    }
}
// DFS算法
void DFS(int v)
{
    vis[v] = true;

    cout << vertex[v].name << " ";

    Edge* p = head[v];

    while (p)
    {
        if (!vis[p->to])
        {
            DFS(p->to);
        }

        p = p->next;
    }
}

// 连通分量编号
int componentId[MAXV];
// 连通分量数量
int componentCount;
// 判断图是否连通
bool isConnected()
{
    for (int i = 1; i <= vertexCount; i++)
    {
        vis[i] = false;
    }

    DFS(1);

    for (int i = 1; i <= vertexCount; i++)
    {
        if (!vis[i])
        {
            return false;
        }
    }

    return true;
}

void testConnected()
{
    cout << "\n===== 连通性检测 =====\n";

    if (isConnected())
    {
        cout << "\n图是连通图\n";
    }
    else
    {
        cout << "\n图不是连通图\n";
    }
}

// DFS标记连通分量
void markComponent(int v, int id)
{
    vis[v] = true;

    componentId[v] = id;

    Edge* p = head[v];

    while (p != NULL)
    {
        if (!vis[p->to])
        {
            markComponent(p->to, id);
        }

        p = p->next;
    }
}
void buildComponents(bool show)
{
    for (int i = 1; i <= vertexCount; i++)
    {
        vis[i] = false;
    }

    componentCount = 0;

    for (int i = 1; i <= vertexCount; i++)
    {
        if (!vis[i])
        {
            componentCount++;

            if (show)
            {
                cout << "\n连通分量 "
                    << componentCount
                    << " : ";
            }

            markComponent(i, componentCount);

            if (show)
            {
                for (int j = 1; j <= vertexCount; j++)
                {
                    if (componentId[j] == componentCount)
                    {
                        cout << vertex[j].name << " ";
                    }
                }

                cout << endl;
            }
        }
    }
}
// 统计连通分量
void connectedComponents()
{
    cout << "\n===== 连通分量 =====\n";
    buildComponents(true);
    cout << "\n共有 " << componentCount << " 个连通分量\n";
}
// 距离统计
int calculateComponentDistance(int comp)
{
    int total = 0;

    bool used[MAXV];

    memset(used, false, sizeof(used));

    int current = -1;

    for (int i = 1; i <= vertexCount; i++)
    {
        if (componentId[i] == comp)
        {
            current = i;

            used[i] = true;

            break;
        }
    }

    if (current == -1)
    {
        return 0;
    }

    while (true)
    {
        int next = -1;

        int minDist = INF;

        for (int i = 1; i <= vertexCount; i++)
        {
            if (componentId[i] == comp &&
                !used[i] &&
                distFloyd[current][i] < minDist)
            {
                minDist = distFloyd[current][i];

                next = i;
            }
        }

        if (next == -1)
        {
            break;
        }

        total += minDist;

        used[next] = true;

        current = next;
    }

    return total;
}
// 换乘规则
void disconnectedTour()
{
    buildComponents(false);

    if (componentCount == 1)
    {
        cout << "\n当前地图是连通图！\n";

        return;
    }
    initFloyd();
    floyd();
    cout << "\n===== 非连通图游览规划 =====\n";

    cout << "共有 " << componentCount << " 个连通分量\n";

    cout << "最少换乘次数：" << componentCount - 1 << endl;
    int totalDistance = 0;

    for (int k = 1; k <= componentCount; k++)
    {
        cout << "\n连通分量 " << k << " ：\n";

        for (int i = 1; i <= vertexCount; i++)
        {
            if (componentId[i] == k)
            {
                cout << vertex[i].name << " ";
            }
        }

        cout << endl;
        int d = calculateComponentDistance(k);
        cout << "分量距离：" << d << " m\n";
        totalDistance += d;
        if (d == 0)
            cout << "(换乘步行距离不计)\n";
        if (k != componentCount)
        {
            cout << "\n------ 换乘 ------\n";
        }
    }
    cout << "\n总距离：" << totalDistance << " m\n";
}

// 打卡路线
int tour[MAXV];

// 路线长度
int tourCnt;

// 打卡路线规划
void planTour(int start)
{
    initFloyd();

    floyd();

    bool visitedTour[MAXV];

    memset(visitedTour, false, sizeof(visitedTour));

    tourCnt = 0;

    int current = start;

    visitedTour[current] = true;

    tour[tourCnt++] = current;

    for (int k = 1; k < vertexCount; k++)
    {
        int next = -1;

        int minDist = INF;

        for (int i = 1; i <= vertexCount; i++)
        {
            if (!visitedTour[i] &&
                distFloyd[current][i] < minDist)
            {
                minDist = distFloyd[current][i];
                next = i;
            }
        }

        if (next == -1)
            break;

        visitedTour[next] = true;

        tour[tourCnt++] = next;

        current = next;
    }

    cout << "\n===== 校园打卡路线 =====\n";

    int totalDistance = 0;

    for (int i = 0; i < tourCnt - 1; i++)
    {
        int u = tour[i];
        int v = tour[i + 1];

        int d = distFloyd[u][v];

        cout
            << vertex[u].name
            << " -> "
            << vertex[v].name
            << " ("
            << d
            << "m)"
            << endl;

        totalDistance += d;
    }

    cout << "\n总距离："
        << totalDistance
        << " m"
        << endl;
}
// 修改道路长度
void modifyRoad(int u, int v, int newWeight)
{
    adjMatrix[u][v] = newWeight;
    adjMatrix[v][u] = newWeight;

    Edge* p = head[u];

    while (p)
    {
        if (p->to == v)
        {
            p->weight = newWeight;
            break;
        }

        p = p->next;
    }

    p = head[v];

    while (p)
    {
        if (p->to == u)
        {
            p->weight = newWeight;
            break;
        }

        p = p->next;
    }

    cout << "道路修改成功！" << endl;
}
// 添加道路
void addRoad(int u, int v, int w)
{
    insertRoad(u, v, w);

    cout << "道路添加成功！" << endl;
    edgeCount++;
}
// 删除道路
void deleteEdgeNode(int u, int v)
{
    Edge* p = head[u];
    Edge* pre = NULL;

    while (p)
    {
        if (p->to == v)
        {
            if (pre == NULL)
            {
                head[u] = p->next;
            }
            else
            {
                pre->next = p->next;
            }

            return;
        }

        pre = p;
        p = p->next;
    }
}
void deleteRoad(int u, int v)
{
    adjMatrix[u][v] = INF;
    adjMatrix[v][u] = INF;

    deleteEdgeNode(u, v);
    deleteEdgeNode(v, u);

    cout << "道路删除成功！" << endl;
    edgeCount--;
}
void pauseScreen()
{
    cout << "\n\n按 Enter 键返回菜单...";

    cin.ignore(numeric_limits<streamsize>::max(), '\n');
    cin.get();

    system("cls");
}
void menu()
{
    cout << "\n";
    cout << "=================================\n";
    cout << "      校园导航系统\n";
    cout << "=================================\n";

    cout << "basic fuction:\n";
    cout << "1. 查看景点信息\n";
    cout << "2. 查看邻接表\n";
    cout << "3. 查看邻接矩阵\n";

    cout << "4. 查询两点间最短路径\n";
    cout << "5. 查询单源点到其他地点的最短路径\n";
    cout << "6. 所有点对最短路径矩阵\n";

    cout << "7. 连通性检测\n";
    cout << "8. 连通分量统计\n";
    cout << "9. 校园打卡路线推荐\n";
    cout << "10.换乘后路线推荐\n";

    cout << "11. 修改道路\n";
    cout << "12. 添加道路\n";
    cout << "13. 删除道路\n";

    cout << "extra function\n";

	cout << "14. 游览模拟\n";
    cout << "15. 最热门地点top5统计\n";
    cout << "0. 退出\n";

    cout << "=================================\n";
}

// 游览模拟
void travel() {
    initFloyd();
    floyd();
    int start, end;
    printVertex();
    cout << "请输入游览的起点编号：";
    cin >> start;
    if (start < 1 || start > vertexCount) {
        cout << "起点编号无效！" << endl;
        return;
    }
    cout << "请输入游览的终点编号：";
    cin >> end;
    if (end < 1 || end > vertexCount) {
        cout << "终点编号无效！" << endl;
        return;
    }
    cout << "\n========== 游览开始 ==========" << endl;
    cout << "出发地：" << vertex[start].name << endl;
    cout << "简介：" << vertex[start].description << endl;
    vertex[start].timeOfVisit++;

    int fullRoute[MAXV * MAXV];
    int routeLen = 0;
    fullRoute[routeLen++] = start;
    int totalDistance = 0;
    int current = start;

    while (true) {
        int dist = distFloyd[current][end];
        bool reachable = (dist != INF);
        int segPath[MAXV];
        int segLen = 0;

        if (reachable) {
            int cur = current;
            segPath[segLen++] = cur;
            while (cur != end) {
                cur = nextFloyd[cur][end];
                segPath[segLen++] = cur;
            }
            totalDistance += dist;
        }
        else {
            segPath[segLen++] = current;
            segPath[segLen++] = end;
        }

        int startIdx = 0;
        if (routeLen > 0 && fullRoute[routeLen - 1] == segPath[0]) {
            startIdx = 1;
        }
        for (int i = startIdx; i < segLen; i++) {
            fullRoute[routeLen++] = segPath[i];
        }

        cout << "\n>>> 到达【" << vertex[end].name << "】" << endl;
        cout << "简介：" << vertex[end].description << endl;
        vertex[end].timeOfVisit++;

        if (reachable) {
            cout << "本段距离：" << dist << " m" << endl;
            cout << "路径：";
            for (int i = 0; i < segLen; i++) {
                if (i > 0) cout << " -> ";
                cout << vertex[segPath[i]].name;
            }
            cout << endl;
        }
        else {
            cout << "注意：需要换乘" << endl;
            cout << "路径：" << vertex[current].name << " -> [换乘] -> " << vertex[end].name << endl;
        }

        cout << "\n累计游览距离：" << totalDistance << " m" << endl;
        cout << "当前游览轨迹：";
        for (int i = 0; i < routeLen; i++) {
            if (i > 0) cout << " -> ";
            cout << vertex[fullRoute[i]].name;
        }
        cout << endl;

        current = end;

        printVertex();
        cout << "请输入下一个要去的景点编号（输入 0 结束游览）：";
        cin >> end;
        if (end == 0) {
            cout << "\n========== 游览结束 ==========" << endl;
            cout << "总游览距离：" << totalDistance << " m" << endl;
            cout << "完整路线：";
            for (int i = 0; i < routeLen; i++) {
                if (i > 0) cout << " -> ";
                cout << vertex[fullRoute[i]].name;
            }
            cout << "\n感谢游览，再见！" << endl;
            break;
        }
        if (end < 1 || end > vertexCount) {
            cout << "编号无效，游览结束。" << endl;
            break;
        }
    }
}

// 最热门地点统计
void hotplacesTop5() {
    cout << "\n========== 最热门地点 Top 5 ==========\n";
    pair<int, int> visitCounts[MAXV];

    for (int i = 1; i <= vertexCount; i++) {
        visitCounts[i - 1] = {vertex[i].timeOfVisit, i};
    }

    sort(visitCounts, visitCounts + vertexCount, [](const pair<int, int>& a, const pair<int, int>& b) {
        return a.first > b.first;
    });

    for (int i = 0; i < min(5, vertexCount); i++) {
        int idx = visitCounts[i].second;
        cout << i + 1 << ". " << vertex[idx].name << " - 游览次数: " << vertex[idx].timeOfVisit << endl;
    }
}

// 主函数

int main()
{
    // 初始化头指针
    memset(head, NULL, sizeof(head));

    // 初始化邻接矩阵
    initMatrix();

    // 导入地图
    loadMap("地图数据.txt");

    int choice;

    while (true)
    {
        menu();

        cin >> choice;

        if (choice == 0)
            break;

        switch (choice)
        {
        case 1:
            printVertex();
            break;

        case 2:
            printAdjList();
            break;

        case 3:
            printAdjMatrix();
            break;

        case 4:
        {
            int s, e;

            cout << "起点编号:";
            cin >> s;

            cout << "终点编号:";
            cin >> e;

            initFloyd();
            floyd();

            shortestPath(s, e);

            break;
        }

        case 5:
        {
            int s;

            cout << "请输入起点:";
            cin >> s;

            dijkstra(s);

            printDijkstraResult(s);

            break;
        }
        case 6:
        {
            initFloyd();

            floyd();

            printFloydMatrix();

            break;
        }
        case 7:
            testConnected();
            break;

        case 8:
            connectedComponents();
            break;

        case 9:
        {
            int start;

            cout << "请输入起点编号：";
            cin >> start;

            if (start < 1 || start > vertexCount)
            {
                cout << "输入错误！" << endl;
                break;
            }

            planTour(start);

            break;
        }
        case 10:
            disconnectedTour();
            break;
        case 11:
        {
            int u, v, w;

            cin >> u >> v >> w;

            modifyRoad(u, v, w);

            break;
        }

        case 12:
        {
            int u, v, w;

            cin >> u >> v >> w;

            addRoad(u, v, w);

            break;
        }

        case 13:
        {
            int u, v;

            cin >> u >> v;

            deleteRoad(u, v);

            break;
        }

        case 14:
        {
            travel();

            break;
        }

        case 15:
        {
            hotplacesTop5();

            break;
        }
        }
        pauseScreen();
    }

    return 0;
}
