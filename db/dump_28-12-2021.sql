--
-- PostgreSQL database cluster dump
--

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:aBz7DZTLd0On/RWFcfJmyA==$QYD34msJ4TBThMNQby04OND4ZlkFk/Zjho/6Y+AX7f4=:vufPSRRUOHdDK2A5fd1PP7dwFebHIqifx9bR5JXBfsc=';






--
-- Databases
--

--
-- Database "template1" dump
--

\connect template1

--
-- PostgreSQL database dump
--

-- Dumped from database version 14.1 (Debian 14.1-1.pgdg110+1)
-- Dumped by pg_dump version 14.1 (Debian 14.1-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- PostgreSQL database dump complete
--

--
-- Database "postgres" dump
--

\connect postgres

--
-- PostgreSQL database dump
--

-- Dumped from database version 14.1 (Debian 14.1-1.pgdg110+1)
-- Dumped by pg_dump version 14.1 (Debian 14.1-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- PostgreSQL database dump complete
--

--
-- Database "yfinance" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 14.1 (Debian 14.1-1.pgdg110+1)
-- Dumped by pg_dump version 14.1 (Debian 14.1-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: yfinance; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE yfinance WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.utf8';


ALTER DATABASE yfinance OWNER TO postgres;

\connect yfinance

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.history (
    id integer NOT NULL,
    ticker character varying(7) NOT NULL,
    price_min double precision,
    price_max double precision,
    net_income boolean,
    date_update date
);


ALTER TABLE public.history OWNER TO postgres;

--
-- Name: history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.history_id_seq OWNER TO postgres;

--
-- Name: history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.history_id_seq OWNED BY public.history.id;


--
-- Name: price; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.price (
    id integer NOT NULL,
    ticker character varying(7) NOT NULL,
    price_now double precision
);


ALTER TABLE public.price OWNER TO postgres;

--
-- Name: price_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.price_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.price_id_seq OWNER TO postgres;

--
-- Name: price_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.price_id_seq OWNED BY public.price.id;


--
-- Name: stock; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stock (
    id integer NOT NULL,
    ticker character varying(7) NOT NULL
);


ALTER TABLE public.stock OWNER TO postgres;

--
-- Name: stock_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stock_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.stock_id_seq OWNER TO postgres;

--
-- Name: stock_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stock_id_seq OWNED BY public.stock.id;


--
-- Name: valuation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.valuation (
    id integer NOT NULL,
    ticker character varying(7) NOT NULL,
    price_target double precision,
    payout double precision
);


ALTER TABLE public.valuation OWNER TO postgres;

--
-- Name: valuation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.valuation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.valuation_id_seq OWNER TO postgres;

--
-- Name: valuation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.valuation_id_seq OWNED BY public.valuation.id;


--
-- Name: history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.history ALTER COLUMN id SET DEFAULT nextval('public.history_id_seq'::regclass);


--
-- Name: price id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.price ALTER COLUMN id SET DEFAULT nextval('public.price_id_seq'::regclass);


--
-- Name: stock id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock ALTER COLUMN id SET DEFAULT nextval('public.stock_id_seq'::regclass);


--
-- Name: valuation id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.valuation ALTER COLUMN id SET DEFAULT nextval('public.valuation_id_seq'::regclass);


--
-- Data for Name: history; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (2, 'APER3', 26.5, 53.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (3, 'CASH3', 2.6, 12.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (5, 'DASA3', 33.6, 65.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (6, 'TCNO3', 1.8, 7.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (7, 'MAPT4', 37, 49.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (8, 'RCSL4', 1.3, 2.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (9, 'TCNO4', 1.5, 6.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (10, 'NORD3', 13.1, 26, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (11, 'FRTA3', 5.6, 10.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (12, 'EMBR3', 17.3, 26, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (13, 'ELMD3', 9.7, 22.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (14, 'OMGE3', 26.2, 39.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (15, 'RRRP3', 27.6, 48.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (16, 'VLID3', 7.1, 11, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (17, 'ORVR3', 21.8, 30.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (18, 'TXRX3', 29.8, 36.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (19, 'ECOR3', 8.1, 13.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (20, 'TELB3', 44.5, 76, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (22, 'DTCY3', 7.1, 12.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (23, 'HBRE3', 8.9, 18, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (24, 'SMFT3', 17, 32.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (25, 'WEST3', 3.1, 10.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (26, 'FRIO3', 41, 72.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (27, 'BIOM3', 12.2, 16.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (28, 'MEAL3', 2.6, 4.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (29, 'AMAR3', 3.4, 10, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (30, 'MSPA3', 48, 48.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (31, 'OPCT3', 2.5, 9.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (32, 'MSPA4', 42.1, 46, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (33, 'TELB4', 15.9, 34.7, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (34, 'BLUT3', 1.9, 6.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (35, 'TXRX4', 8.4, 10.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (36, 'ENJU3', 2.8, 11.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (37, 'MBLY3', 4.4, 17.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (39, 'BAHI3', 13, 16.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (40, 'PINE4', 1.7, 3.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (41, 'ALPK3', 3.9, 8.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (42, 'CTNM3', 9.1, 13, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (43, 'BKBR3', 6.6, 12.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (44, 'ADHM3', 1.6, 1.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (45, 'AHEB3', 25, 28.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (46, 'AHEB5', 18, 23, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (47, 'CEED3', 40, 61.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (48, 'ESTR4', 51, 80.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (49, 'BLUT4', 0.9, 4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (50, 'CRDE3', 17, 28, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (51, 'SGPS3', 5.2, 14.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (52, 'VIVR3', 1.3, 9.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (53, 'SHOW3', 3.2, 7.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (54, 'AZUL4', 21.9, 48.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (56, 'OIBR4', 1.4, 2.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (57, 'TCSA3', 3.2, 9.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (59, 'GOLL4', 14.8, 27.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (60, 'PLAS3', 8.9, 19.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (61, 'OIBR3', 0.8, 1.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (62, 'HOOT4', 2.8, 5.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (63, 'GSHP3', 35.3, 43.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (64, 'COGN3', 2.3, 4.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (65, 'PMAM3', 8.7, 18, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (66, 'ATMP3', 3.2, 9.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (67, 'AVLL3', 18, 31.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (68, 'RPMG3', 2.7, 6.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (69, 'MTIG4', 32, 89.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (70, 'INEP3', 1.3, 3.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (71, 'INEP4', 1.3, 3.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (73, 'JFEN3', 1, 6.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (74, 'IGBR3', 25, 128, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (75, 'BDLL3', 9.6, 15, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (76, 'BDLL4', 10.2, 16.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (77, 'SNSY5', 4.8, 7.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (78, 'SLED3', 0.6, 1.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (79, 'PDGR3', 1.4, 7.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (80, 'TEKA3', 26.1, 40.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (81, 'SLED4', 0.3, 0.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (82, 'OSXB3', 6.5, 12.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (83, 'LLIS3', 1.2, 4.7, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (84, 'TEKA4', 8.4, 21.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (85, 'HETA4', 9.9, 17.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (86, 'ARML3', 19, 26.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (87, 'BRBI11', 16.4, 28.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (88, 'BRIT3', 5.3, 13.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (90, 'CLSA3', 8.8, 29.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (91, 'DESK3', 15.1, 26.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (92, 'DOTZ3', 3.2, 17.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (93, 'FIQE3', 5.6, 8.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (94, 'GETT3', 1.8, 3.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (95, 'GETT4', 1.6, 3.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (96, 'GGPS3', 14, 19.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (97, 'IFCM3', 13.1, 23.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (98, 'KRSA3', 4.4, 8.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (99, 'LVTC3', 15.5, 26.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (100, 'MATD3', 14, 21.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (101, 'MLAS3', 6.3, 13, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (102, 'MODL11', 10.2, 18.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (103, 'MODL3', 3.9, 5.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (104, 'MODL4', 3.1, 4.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (105, 'NINJ3', 3.3, 27, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (107, 'PORT3', 58.7, 71, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (108, 'RECV3', 13.6, 20.7, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (109, 'TRAD3', 5.4, 13.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (110, 'TTEN3', 6.9, 12.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (111, 'VVEO3', 16.4, 27.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (112, 'MWET4', 11.5, 40.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (113, 'MWET3', 22.5, 69.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (114, 'MGEL4', 13.1, 26.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (115, 'CEBR5', -16.5, 24.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (116, 'CEBR6', -18.8, 24.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (117, 'CEBR3', -13.8, 26.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (118, 'RSID3', 7.9, 14.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (119, 'GPIV33', 5.3, 7.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (120, 'TPIS3', 1.8, 3.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (58, 'BAHI11', 10000, 10000, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (122, 'LUPA3', 4.2, 8.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (123, 'CTKA4', 13.8, 32.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (125, 'BRKM6', 30.4, 43.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (126, 'HBTS5', 48, 81.7, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (127, 'AZEV3', 3.5, 8.7, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (128, 'USIM3', 11.7, 20.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (129, 'BAZA3', 37.1, 41.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (130, 'CSNA3', 19.8, 46.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (131, 'USIM5', 12.1, 20.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (132, 'RNEW4', 2.1, 6.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (133, 'RNEW11', 6.7, 20.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (134, 'HAGA4', 1.8, 3.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (135, 'RNEW3', 2.3, 6.7, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (136, 'CLSC3', 60, 94.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (137, 'EUCA4', 8, 11.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (138, 'CTKA3', 22.5, 29.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (139, 'GOAU3', 8.4, 11.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (140, 'MNDL3', 34.3, 69, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (142, 'PETR4', 21.9, 29.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (143, 'USIM6', 19, 22.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (144, 'PETR3', 22.5, 31.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (145, 'CPLE11', 26.9, 33.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (146, 'MRFG3', 17.3, 27.7, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (147, 'GGBR3', 17.9, 24.7, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (148, 'CPLE6', 5.5, 6.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (149, 'TKNO4', 54.5, 69, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (150, 'GOAU4', 9.5, 12.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (151, 'ETER3', 13.4, 28.7, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (152, 'PEAB4', 54.9, 79.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (153, 'BRKM3', 39.6, 58.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (154, 'CLSC4', 65.5, 78.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (155, 'BRKM5', 40.9, 62.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (156, 'DOHL4', 5.5, 7.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (157, 'CESP3', 21.9, 28.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (159, 'BOBR4', 1.7, 3.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (160, 'BRAP3', 42.4, 59.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (161, 'CESP6', 22.6, 26.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (162, 'TASA4', 20.2, 28.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (163, 'GGBR4', 22.2, 29.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (164, 'TASA3', 20.6, 28.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (165, 'BRAP4', 44.9, 70.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (166, 'PCAR3', 21.7, 41.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (167, 'PEAB3', 50.7, 79.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (168, 'BGIP4', 22.4, 25.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (169, 'EUCA3', 12.9, 21.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (170, 'RAPT4', 10.2, 15, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (171, 'VALE3', 62.3, 106.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (172, 'JHSF3', 4.6, 7.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (173, 'DEXP4', 7, 15.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (174, 'ALLD3', 14.6, 37.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (176, 'TRPL4', 21.8, 25.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (177, 'RAPT3', 11.3, 13.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (178, 'EPAR3', 11.3, 20.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (179, 'DEXP3', 8.1, 16.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (180, 'BRSR6', 9.9, 14, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (181, 'JBSS3', 26.5, 38, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (182, 'EALT4', 5.6, 7.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (183, 'CEDO4', 5.3, 8.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (184, 'ENAT3', 11.7, 18.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (185, 'CEPE5', 25, 31, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (186, 'CTSA4', 1.4, 3.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (187, 'BNBR3', 65.2, 71.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (188, 'POSI3', 8.4, 14.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (189, 'CGRA4', 32.8, 49.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (190, 'CGRA3', 32.3, 50.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (191, 'ROMI3', 14.6, 26.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (193, 'TAEE11', 33.9, 39.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (194, 'TAEE4', 11.3, 13, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (195, 'TAEE3', 11.3, 13, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (196, 'PATI3', 67, 86, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (197, 'LAVV3', 4.6, 8.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (198, 'ALUP3', 7.8, 9.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (199, 'SAPR3', 3.5, 4.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (200, 'NEOE3', 14.6, 18.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (201, 'ALUP11', 23.6, 27.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (202, 'POMO3', 2.3, 3.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (203, 'BRSR3', 11.4, 15, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (204, 'ALUP4', 7.9, 9.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (205, 'CEPE6', 26.1, 32, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (206, 'BGIP3', 31, 40, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (207, 'SAPR11', 18.2, 20.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (208, 'CESP5', 30, 42, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (210, 'BBAS3', 27.6, 34.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (211, 'UNIP5', 71.4, 98, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (212, 'BMEB4', 8.8, 10.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (213, 'UNIP6', 70.8, 97.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (214, 'VBBR3', 21, 29.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (215, 'CSRN5', 14.9, 25.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (216, 'ENGI4', 6.4, 7.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (217, 'CEEB3', 31.9, 53.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (218, 'UNIP3', 75.5, 100.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (219, 'TRPL3', 29, 33.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (220, 'CMIG4', 11.4, 15.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (221, 'MDNE3', 4.5, 10.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (222, 'HBOR3', 4.2, 9.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (223, 'PTNT4', 5.2, 7.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (224, 'MNPR3', 6.8, 25, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (225, 'CSRN3', 15.7, 25.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (227, 'POMO4', 2.6, 3.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (228, 'LIGT3', 9.7, 16.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (229, 'ENBR3', 17.1, 21.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (230, 'HAGA3', 3.2, 7.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (231, 'CYRE3', 13.2, 25.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (232, 'PLPL3', 3, 6.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (233, 'GEPA3', 31.5, 38.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (234, 'GEPA4', 31.5, 37.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (235, 'EKTR4', 24.8, 31.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (236, 'BEES3', 4.6, 5.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (237, 'CRPG6', 55, 119.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (238, 'CTSA3', 1.9, 3.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (239, 'SUZB3', 48.4, 62.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (240, 'PFRM3', 4.6, 6.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (242, 'LPSB3', 2.2, 4.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (243, 'EQTL3', 22.6, 26.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (245, 'TRIS3', 5.2, 10.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (246, 'CSRN6', 14.4, 53.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (247, 'AGRO3', 23.3, 30.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (248, 'SLCE3', 37, 53.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (249, 'CSMG3', 12.5, 16.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (250, 'CEAB3', 6.1, 15.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (251, 'CRPG5', 53, 118.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (252, 'PTBL3', 8.3, 18, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (253, 'ENGI11', 39.3, 49.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (254, 'LEVE3', 28.5, 43.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (255, 'WIZS3', 7.8, 18.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (256, 'MTSA4', 34.3, 53.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (257, 'ITSA4', 9.6, 11.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (258, 'RANI3', 5.9, 9.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (259, 'ITSA3', 9.7, 12.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (260, 'BBDC3', 16.5, 23.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (262, 'CMIG3', 13.6, 19, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (263, 'CRIV3', 4.8, 6.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (264, 'ESPA3', 7.7, 21.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (265, 'MYPK3', 13.6, 19.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (266, 'LOGG3', 22, 33.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (267, 'SANB3', 15, 21, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (268, 'ABCB4', 14.3, 17.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (269, 'BRSR5', 15.8, 19.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (270, 'BEES4', 5.6, 6.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (271, 'SHUL4', 8.2, 11.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (272, 'CSAN3', 19.8, 27.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (273, 'EEEL4', 350, 699, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (274, 'EMAE4', 51.7, 97, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (275, 'KLBN4', 4.1, 5.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (276, 'CURY3', 6.4, 10.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (277, 'ITUB3', 19.9, 28.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (279, 'BPAC5', 4.6, 8.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (280, 'SANB11', 32, 43.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (281, 'EQMA3B', 41.5, 44.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (282, 'KLBN11', 22, 26.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (283, 'SEER3', 10, 19, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (284, 'EEEL3', 325, 560, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (285, 'MRVE3', 10, 17.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (286, 'CAML3', 8.5, 10.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (287, 'BBDC4', 19, 27.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (288, 'VULC3', 7.9, 10.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (289, 'RSUL4', 31.2, 99, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (290, 'ELET6', 31.7, 47.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (291, 'MOAR3', 278.7, 431, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (292, 'EALT3', 11.1, 15.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (293, 'CRIV4', 5.3, 6.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (294, 'ITUB4', 22, 32.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (296, 'ELET3', 32.1, 47.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (297, 'DXCO3', 18.1, 23.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (298, 'JSLG3', 6.6, 12.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (299, 'FESA4', 37.9, 58.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (300, 'FRAS3', 11.8, 17.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (301, 'MOVI3', 14.9, 22.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (302, 'TGMA3', 13, 25.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (303, 'WHRL3', 6.2, 7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (304, 'EZTC3', 17.7, 34.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (305, 'REDE3', 6.3, 8.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (306, 'BEEF3', 7.5, 10.7, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (307, 'CARD3', 11.8, 25.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (308, 'EKTR3', 32.7, 46, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (309, 'BRIV4', 7.4, 9.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (310, 'COCE5', 47.5, 60.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (311, 'BRIV3', 7.7, 10.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (313, 'CRFB3', 14.5, 23, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (314, 'GUAR3', 9.8, 22.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (315, 'DOHL3', 17.5, 29.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (316, 'CGAS3', 140, 180, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (317, 'SBSP3', 31.7, 39.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (318, 'FESA3', 47.8, 59.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (319, 'COCE3', 55, 85, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (320, 'CGAS5', 137.2, 186.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (321, 'ASAI3', 12.4, 19.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (322, 'CSAB4', 40, 51, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (323, 'PSSA3', 21.5, 28.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (324, 'KLBN3', 5.4, 6.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (325, 'KEPL3', 30.5, 45.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (326, 'AURA33', 43, 69.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (327, 'UCAS3', 3.9, 5.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (328, 'LOGN3', 14.4, 22.7, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (330, 'DIRR3', 9.5, 15, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (331, 'WHRL4', 7.4, 8.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (332, 'PDTC3', 4.8, 8.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (333, 'SIMH3', 10, 17.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (334, 'GRND3', 8.2, 12.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (335, 'BPAC11', 19.9, 32.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (336, 'TIMS3', 11.2, 14.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (337, 'GFSA3', 1.9, 4.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (338, 'PRNR3', 6.3, 10.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (339, 'BSLI4', 13.8, 25.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (340, 'EQPA3', 4.7, 5.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (341, 'BBSE3', 18.4, 24.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (342, 'SMTO3', 29.3, 40.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (343, 'JALL3', 8.5, 10.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (344, 'QUAL3', 15.1, 29.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (345, 'PARD3', 18.5, 25.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (347, 'SOJA3', 13, 15.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (348, 'TUPY3', 19, 24.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (349, 'ENGI3', 13.7, 18.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (350, 'TEND3', 16.5, 26.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (351, 'AESB3', 10.9, 15.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (352, 'EGIE3', 35.2, 40.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (353, 'OFSA3', 25, 37.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (354, 'ENEV3', 13.8, 18, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (355, 'LCAM3', 19.7, 29.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (356, 'EVEN3', 6, 10.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (357, 'WLMM3', 31.9, 44.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (358, 'HYPE3', 26.8, 36.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (359, 'SOND5', 34.5, 52.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (360, 'CXSE3', 7.6, 13, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (362, 'TECN3', 2.2, 4.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (363, 'CAMB3', 3.6, 6.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (364, 'WLMM4', 30, 42.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (365, 'CPLE5', 6, 54.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (366, 'BRPR3', 6.9, 9.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (367, 'B3SA3', 11, 16.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (368, 'ENMT3', 54.7, 80, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (369, 'ENMT4', 54.7, 80.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (370, 'MRSA3B', 35.7, 42, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (372, 'PRIO3', 16.8, 28.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (373, 'ELET5', 63.2, 80.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (374, 'ABEV3', 15, 19.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (375, 'MELK3', 3.3, 6.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (376, 'LAME3', 4.4, 21.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (377, 'LAME4', 4.6, 22.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (378, 'EQPA7', 4.5, 9.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (379, 'EQPA5', 5.5, 9.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (380, 'MDIA3', 27.4, 33.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (381, 'BSLI3', 25.8, 36.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (382, 'IGTA3', 28.6, 44.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (383, 'GPAR3', 40, 65, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (384, 'VITT3', 8.9, 13.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (385, 'ODPV3', 11.8, 16.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (386, 'GMAT3', 5.7, 8.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (387, 'VIVT3', 40.5, 53, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (388, 'AGXY3', 7, 10.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (389, 'BALM4', 12.8, 21.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (390, 'MRSA5B', 33, 45.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (392, 'INTB3', 24.8, 33.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (393, 'BMOB3', 12.8, 25.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (394, 'UGPA3', 12.4, 20.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (395, 'BLAU3', 33.2, 53.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (396, 'BPAN4', 10.8, 25.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (397, 'WSON33', 61.4, 68.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (399, 'JOPA3', 27, 38.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (400, 'PGMN3', 7.9, 13.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (401, 'JPSA3', 24.4, 36.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (402, 'BALM3', 15.8, 20.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (403, 'RENT3', 45.3, 68.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (404, 'BRGE12', 5.6, 7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (405, 'BPAC3', 12.8, 21, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (406, 'MTRE3', 5.7, 12.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (407, 'BAUH4', 77, 89.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (408, 'VIVA3', 23.8, 34.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (409, 'RAIZ4', 5.5, 7.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (410, 'BMIN4', 17, 21, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (411, 'RPAD6', 4.3, 6.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (412, 'POWE3', 10, 18.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (413, 'RDNI3', 9.9, 12.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (414, 'MILS3', 5, 8.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (416, 'PNVL3', 12, 21.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (417, 'JOPA4', 37, 74.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (418, 'BOAS3', 6.2, 13.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (419, 'BMKS3', 222, 250, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (420, 'LJQQ3', 9.7, 24.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (421, 'BRGE11', 7.6, 10.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (422, 'BRGE3', 7.5, 9.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (423, 'SULA4', 8.1, 11.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (424, 'RPAD3', 5.9, 7.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (425, 'SBFG3', 20.9, 39.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (426, 'SULA11', 24.4, 36.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (427, 'LUXM4', 71.5, 81.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (428, 'SULA3', 8.2, 13.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (429, 'AFLT3', 8.5, 10.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (430, 'TFCO4', 10.8, 16.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (431, 'IGTI3', 24.4, 36.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (433, 'STBP3', 5.2, 9.9, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (434, 'CSED3', 6, 16.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (435, 'IGTI11', 179, 208.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (436, 'BMIN3', 19.7, 25, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (437, 'MULT3', 17.3, 26.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (438, 'BRGE8', 9.7, 10.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (439, 'NGRD3', 2.7, 7.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (440, 'AMBP3', 31.6, 70, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (441, 'CCRO3', 11, 13.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (442, 'ALSO3', 19.2, 32.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (443, 'VAMO3', 10.4, 17.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (444, 'BRML3', 7, 11.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (445, 'SOMA3', 12.7, 20.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (446, 'MOSI3', 8.4, 20.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (447, 'CEGR3', 58, 61, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (448, 'BRFS3', 19.2, 30.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (450, 'WEGE3', 32.2, 41.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (451, 'SCAR3', 33.2, 43.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (452, 'ALPA3', 32, 52.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (453, 'DMVF3', 4.5, 10.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (454, 'RADL3', 21.2, 27.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (455, 'ALPA4', 38, 60.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (456, 'LREN3', 28.3, 43.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (457, 'CVCB3', 13.2, 28.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (458, 'TOTS3', 29.8, 40.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (459, 'YDUQ3', 20.9, 35.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (460, 'AALR3', 9.4, 18.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (461, 'RAIL3', 16, 21.7, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (462, 'MGLU3', 6.4, 23.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (463, 'NTCO3', 25.7, 61, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (464, 'MERC4', 10, 13.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (465, 'RDOR3', 47.7, 75.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (467, 'AERI3', 7, 10.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (468, 'ANIM3', 6.6, 14.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (469, 'HAPV3', 10.3, 15.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (470, 'PETZ3', 18.1, 28.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (471, 'SQIA3', 15.2, 30.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (472, 'CBEE3', 22.5, 25.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (473, 'MERC3', 25, 29.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (474, 'AMER3', 27.4, 72.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (475, 'BIDI3', 11, 28.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (476, 'BIDI11', 32.2, 85.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (477, 'BIDI4', 11, 28.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (478, 'SEQL3', 9.1, 29.1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (479, 'VIIA3', 5.2, 16, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (480, 'LWSA3', 11.7, 27.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (1, 'GNDI3', 58.5, 87.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (4, 'RCSL3', 3.4, 7.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (21, 'HBSA3', 2.6, 6.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (38, 'IRBR3', 4, 6.2, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (55, 'CTNM4', 3.5, 7.5, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (72, 'BBRK3', 1, 4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (89, 'CBAV3', 10.3, 16.3, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (106, 'ONCO3', 7.7, 15.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (121, 'DMMO3', 0.6, 1, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (124, 'AZEV4', 2.8, 8.4, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (141, 'CPLE3', 5.1, 6.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (158, 'FHER3', 14, 46.8, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (175, 'PATI4', 56.8, 91.6, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (192, 'CMIN3', 5.2, 9.4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (209, 'SAPR4', 3.7, 4.2, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (226, 'CEDO3', 6.5, 10.6, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (241, 'CIEL3', 2, 4, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (244, 'BMGB4', 2.8, 5.1, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (261, 'CPFE3', 23.1, 28.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (278, 'ATOM3', 2.8, 7.9, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (295, 'SANB4', 17.2, 22.8, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (312, 'CRPG3', 78.3, 128, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (329, 'BTTL3', 10000, 10000, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (346, 'BMEB3', 9.5, 12.7, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (361, 'FLRY3', 16.9, 27.3, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (398, 'PTNT3', 11.9, 29, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (415, 'ARZZ3', 66.6, 100, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (432, 'LIPR3', 55, 73, false, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (449, 'RPAD5', 7.1, 10.5, true, '2021-12-09');
INSERT INTO public.history (id, ticker, price_min, price_max, net_income, date_update) VALUES (466, 'SYNE3', 9.6, 14.4, false, '2021-12-09');


--
-- Data for Name: price; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.price (id, ticker, price_now) VALUES (2, 'APER3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (3, 'CASH3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (4, 'RCSL3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (5, 'DASA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (6, 'TCNO3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (7, 'MAPT4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (8, 'RCSL4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (9, 'TCNO4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (10, 'NORD3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (11, 'FRTA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (12, 'EMBR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (13, 'ELMD3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (156, 'DOHL4', 5.92);
INSERT INTO public.price (id, ticker, price_now) VALUES (15, 'RRRP3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (16, 'VLID3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (17, 'ORVR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (18, 'TXRX3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (19, 'ECOR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (20, 'TELB3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (21, 'HBSA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (22, 'DTCY3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (23, 'HBRE3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (24, 'SMFT3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (25, 'WEST3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (26, 'FRIO3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (27, 'BIOM3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (28, 'MEAL3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (29, 'AMAR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (30, 'MSPA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (31, 'OPCT3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (32, 'MSPA4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (33, 'TELB4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (34, 'BLUT3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (35, 'TXRX4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (36, 'ENJU3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (37, 'MBLY3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (38, 'IRBR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (39, 'BAHI3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (40, 'PINE4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (41, 'ALPK3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (42, 'CTNM3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (43, 'BKBR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (44, 'ADHM3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (45, 'AHEB3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (46, 'AHEB5', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (47, 'CEED3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (48, 'ESTR4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (49, 'BLUT4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (51, 'SGPS3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (52, 'VIVR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (53, 'SHOW3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (54, 'AZUL4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (55, 'CTNM4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (56, 'OIBR4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (57, 'TCSA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (59, 'GOLL4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (60, 'PLAS3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (61, 'OIBR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (62, 'HOOT4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (63, 'GSHP3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (64, 'COGN3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (65, 'PMAM3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (66, 'ATMP3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (67, 'AVLL3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (68, 'RPMG3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (69, 'MTIG4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (70, 'INEP3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (71, 'INEP4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (72, 'BBRK3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (73, 'JFEN3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (74, 'IGBR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (75, 'BDLL3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (76, 'BDLL4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (77, 'SNSY5', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (78, 'SLED3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (79, 'PDGR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (80, 'TEKA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (81, 'SLED4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (82, 'OSXB3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (83, 'LLIS3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (84, 'TEKA4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (85, 'HETA4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (141, 'CPLE3', 5.97);
INSERT INTO public.price (id, ticker, price_now) VALUES (89, 'CBAV3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (92, 'DOTZ3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (97, 'IFCM3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (98, 'KRSA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (102, 'MODL11', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (103, 'MODL3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (104, 'MODL4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (105, 'NINJ3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (106, 'ONCO3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (108, 'RECV3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (109, 'TRAD3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (112, 'MWET4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (113, 'MWET3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (114, 'MGEL4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (118, 'RSID3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (119, 'GPIV33', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (120, 'TPIS3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (121, 'DMMO3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (122, 'LUPA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (123, 'CTKA4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (124, 'AZEV4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (125, 'BRKM6', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (126, 'HBTS5', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (127, 'AZEV3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (132, 'RNEW4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (133, 'RNEW11', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (134, 'HAGA4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (135, 'RNEW3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (50, 'CRDE3', 15.8);
INSERT INTO public.price (id, ticker, price_now) VALUES (138, 'CTKA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (139, 'GOAU3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (140, 'MNDL3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (142, 'PETR4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (144, 'PETR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (146, 'MRFG3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (147, 'GGBR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (149, 'TKNO4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (150, 'GOAU4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (151, 'ETER3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (86, 'ARML3', 26.4);
INSERT INTO public.price (id, ticker, price_now) VALUES (153, 'BRKM3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (155, 'BRKM5', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (157, 'CESP3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (107, 'PORT3', 55.5);
INSERT INTO public.price (id, ticker, price_now) VALUES (58, 'BAHI11', NULL);
INSERT INTO public.price (id, ticker, price_now) VALUES (88, 'BRIT3', 4.9);
INSERT INTO public.price (id, ticker, price_now) VALUES (90, 'CLSA3', 9.12);
INSERT INTO public.price (id, ticker, price_now) VALUES (91, 'DESK3', 17.34);
INSERT INTO public.price (id, ticker, price_now) VALUES (93, 'FIQE3', 6);
INSERT INTO public.price (id, ticker, price_now) VALUES (94, 'GETT3', 1.86);
INSERT INTO public.price (id, ticker, price_now) VALUES (95, 'GETT4', 1.89);
INSERT INTO public.price (id, ticker, price_now) VALUES (115, 'CEBR5', 15.57);
INSERT INTO public.price (id, ticker, price_now) VALUES (116, 'CEBR6', 16.4);
INSERT INTO public.price (id, ticker, price_now) VALUES (96, 'GGPS3', 15.91);
INSERT INTO public.price (id, ticker, price_now) VALUES (117, 'CEBR3', 16.08);
INSERT INTO public.price (id, ticker, price_now) VALUES (128, 'USIM3', 14.09);
INSERT INTO public.price (id, ticker, price_now) VALUES (129, 'BAZA3', 38.8);
INSERT INTO public.price (id, ticker, price_now) VALUES (130, 'CSNA3', 24.95);
INSERT INTO public.price (id, ticker, price_now) VALUES (143, 'USIM6', 19);
INSERT INTO public.price (id, ticker, price_now) VALUES (145, 'CPLE11', 31.59);
INSERT INTO public.price (id, ticker, price_now) VALUES (154, 'CLSC4', 68);
INSERT INTO public.price (id, ticker, price_now) VALUES (1, 'GNDI3', 59.32);
INSERT INTO public.price (id, ticker, price_now) VALUES (110, 'TTEN3', 9.7);
INSERT INTO public.price (id, ticker, price_now) VALUES (101, 'MLAS3', 8.46);
INSERT INTO public.price (id, ticker, price_now) VALUES (100, 'MATD3', 12.93);
INSERT INTO public.price (id, ticker, price_now) VALUES (99, 'LVTC3', 16.11);
INSERT INTO public.price (id, ticker, price_now) VALUES (137, 'EUCA4', 8.91);
INSERT INTO public.price (id, ticker, price_now) VALUES (131, 'USIM5', 14.75);
INSERT INTO public.price (id, ticker, price_now) VALUES (148, 'CPLE6', 6.4);
INSERT INTO public.price (id, ticker, price_now) VALUES (158, 'FHER3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (159, 'BOBR4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (160, 'BRAP3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (161, 'CESP6', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (162, 'TASA4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (163, 'GGBR4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (164, 'TASA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (165, 'BRAP4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (185, 'CEPE5', 25.08);
INSERT INTO public.price (id, ticker, price_now) VALUES (182, 'EALT4', 6.82);
INSERT INTO public.price (id, ticker, price_now) VALUES (189, 'CGRA4', 37.4);
INSERT INTO public.price (id, ticker, price_now) VALUES (171, 'VALE3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (172, 'JHSF3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (178, 'EPAR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (183, 'CEDO4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (186, 'CTSA4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (190, 'CGRA3', 38.9);
INSERT INTO public.price (id, ticker, price_now) VALUES (188, 'POSI3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (197, 'LAVV3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (191, 'ROMI3', 17.98);
INSERT INTO public.price (id, ticker, price_now) VALUES (208, 'CESP5', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (193, 'TAEE11', 36.29);
INSERT INTO public.price (id, ticker, price_now) VALUES (194, 'TAEE4', 12.15);
INSERT INTO public.price (id, ticker, price_now) VALUES (221, 'MDNE3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (222, 'HBOR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (223, 'PTNT4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (224, 'MNPR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (226, 'CEDO3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (230, 'HAGA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (231, 'CYRE3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (238, 'CTSA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (239, 'SUZB3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (240, 'PFRM3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (242, 'LPSB3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (196, 'PATI3', 70.34);
INSERT INTO public.price (id, ticker, price_now) VALUES (250, 'CEAB3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (258, 'RANI3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (195, 'TAEE3', 12.1);
INSERT INTO public.price (id, ticker, price_now) VALUES (265, 'MYPK3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (198, 'ALUP3', 8.08);
INSERT INTO public.price (id, ticker, price_now) VALUES (275, 'KLBN4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (282, 'KLBN11', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (289, 'RSUL4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (290, 'ELET6', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (291, 'MOAR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (199, 'SAPR3', 3.82);
INSERT INTO public.price (id, ticker, price_now) VALUES (296, 'ELET3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (298, 'JSLG3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (306, 'BEEF3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (200, 'NEOE3', 17.25);
INSERT INTO public.price (id, ticker, price_now) VALUES (314, 'GUAR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (254, 'LEVE3', 32);
INSERT INTO public.price (id, ticker, price_now) VALUES (201, 'ALUP11', 24.16);
INSERT INTO public.price (id, ticker, price_now) VALUES (232, 'PLPL3', 3.2);
INSERT INTO public.price (id, ticker, price_now) VALUES (255, 'WIZS3', 7.9);
INSERT INTO public.price (id, ticker, price_now) VALUES (257, 'ITSA4', 9.08);
INSERT INTO public.price (id, ticker, price_now) VALUES (202, 'POMO3', 2.46);
INSERT INTO public.price (id, ticker, price_now) VALUES (204, 'ALUP4', 8);
INSERT INTO public.price (id, ticker, price_now) VALUES (205, 'CEPE6', 29.99);
INSERT INTO public.price (id, ticker, price_now) VALUES (207, 'SAPR11', 19.19);
INSERT INTO public.price (id, ticker, price_now) VALUES (206, 'BGIP3', 35.78);
INSERT INTO public.price (id, ticker, price_now) VALUES (270, 'BEES4', 5.74);
INSERT INTO public.price (id, ticker, price_now) VALUES (177, 'RAPT3', 12.11);
INSERT INTO public.price (id, ticker, price_now) VALUES (210, 'BBAS3', 29.11);
INSERT INTO public.price (id, ticker, price_now) VALUES (211, 'UNIP5', 99.99);
INSERT INTO public.price (id, ticker, price_now) VALUES (212, 'BMEB4', 10.89);
INSERT INTO public.price (id, ticker, price_now) VALUES (214, 'VBBR3', 21.47);
INSERT INTO public.price (id, ticker, price_now) VALUES (215, 'CSRN5', 15.24);
INSERT INTO public.price (id, ticker, price_now) VALUES (256, 'MTSA4', 42.5);
INSERT INTO public.price (id, ticker, price_now) VALUES (216, 'ENGI4', 7.52);
INSERT INTO public.price (id, ticker, price_now) VALUES (217, 'CEEB3', 33.5);
INSERT INTO public.price (id, ticker, price_now) VALUES (219, 'TRPL3', 31.37);
INSERT INTO public.price (id, ticker, price_now) VALUES (220, 'CMIG4', 13.21);
INSERT INTO public.price (id, ticker, price_now) VALUES (225, 'CSRN3', 15.89);
INSERT INTO public.price (id, ticker, price_now) VALUES (262, 'CMIG3', 17.94);
INSERT INTO public.price (id, ticker, price_now) VALUES (228, 'LIGT3', 11.74);
INSERT INTO public.price (id, ticker, price_now) VALUES (227, 'POMO4', 2.95);
INSERT INTO public.price (id, ticker, price_now) VALUES (229, 'ENBR3', 20.83);
INSERT INTO public.price (id, ticker, price_now) VALUES (266, 'LOGG3', 24.54);
INSERT INTO public.price (id, ticker, price_now) VALUES (234, 'GEPA4', 34.22);
INSERT INTO public.price (id, ticker, price_now) VALUES (233, 'GEPA3', 32);
INSERT INTO public.price (id, ticker, price_now) VALUES (235, 'EKTR4', 28.75);
INSERT INTO public.price (id, ticker, price_now) VALUES (236, 'BEES3', 4.76);
INSERT INTO public.price (id, ticker, price_now) VALUES (237, 'CRPG6', 70.96);
INSERT INTO public.price (id, ticker, price_now) VALUES (245, 'TRIS3', 6.02);
INSERT INTO public.price (id, ticker, price_now) VALUES (246, 'CSRN6', 17.18);
INSERT INTO public.price (id, ticker, price_now) VALUES (247, 'AGRO3', 28.28);
INSERT INTO public.price (id, ticker, price_now) VALUES (248, 'SLCE3', 43.55);
INSERT INTO public.price (id, ticker, price_now) VALUES (249, 'CSMG3', 12.53);
INSERT INTO public.price (id, ticker, price_now) VALUES (251, 'CRPG5', 70.9);
INSERT INTO public.price (id, ticker, price_now) VALUES (260, 'BBDC3', 16.41);
INSERT INTO public.price (id, ticker, price_now) VALUES (252, 'PTBL3', 10.05);
INSERT INTO public.price (id, ticker, price_now) VALUES (253, 'ENGI11', 44.6);
INSERT INTO public.price (id, ticker, price_now) VALUES (264, 'ESPA3', 8.24);
INSERT INTO public.price (id, ticker, price_now) VALUES (263, 'CRIV3', 4.72);
INSERT INTO public.price (id, ticker, price_now) VALUES (267, 'SANB3', 14.47);
INSERT INTO public.price (id, ticker, price_now) VALUES (268, 'ABCB4', 16.14);
INSERT INTO public.price (id, ticker, price_now) VALUES (269, 'BRSR5', 17.9);
INSERT INTO public.price (id, ticker, price_now) VALUES (271, 'SHUL4', 8.65);
INSERT INTO public.price (id, ticker, price_now) VALUES (272, 'CSAN3', 21.45);
INSERT INTO public.price (id, ticker, price_now) VALUES (273, 'EEEL4', 350);
INSERT INTO public.price (id, ticker, price_now) VALUES (276, 'CURY3', 6.94);
INSERT INTO public.price (id, ticker, price_now) VALUES (277, 'ITUB3', 19.38);
INSERT INTO public.price (id, ticker, price_now) VALUES (279, 'BPAC5', 5.12);
INSERT INTO public.price (id, ticker, price_now) VALUES (280, 'SANB11', 30.79);
INSERT INTO public.price (id, ticker, price_now) VALUES (281, 'EQMA3B', 41.35);
INSERT INTO public.price (id, ticker, price_now) VALUES (283, 'SEER3', 10.4);
INSERT INTO public.price (id, ticker, price_now) VALUES (284, 'EEEL3', 375);
INSERT INTO public.price (id, ticker, price_now) VALUES (285, 'MRVE3', 11.79);
INSERT INTO public.price (id, ticker, price_now) VALUES (286, 'CAML3', 10.98);
INSERT INTO public.price (id, ticker, price_now) VALUES (287, 'BBDC4', 19.39);
INSERT INTO public.price (id, ticker, price_now) VALUES (292, 'EALT3', 11.35);
INSERT INTO public.price (id, ticker, price_now) VALUES (288, 'VULC3', 9.57);
INSERT INTO public.price (id, ticker, price_now) VALUES (294, 'ITUB4', 21.48);
INSERT INTO public.price (id, ticker, price_now) VALUES (297, 'DXCO3', 15.32);
INSERT INTO public.price (id, ticker, price_now) VALUES (299, 'FESA4', 50.94);
INSERT INTO public.price (id, ticker, price_now) VALUES (301, 'MOVI3', 16.45);
INSERT INTO public.price (id, ticker, price_now) VALUES (300, 'FRAS3', 13.3);
INSERT INTO public.price (id, ticker, price_now) VALUES (302, 'TGMA3', 15.01);
INSERT INTO public.price (id, ticker, price_now) VALUES (278, 'ATOM3', 2.63);
INSERT INTO public.price (id, ticker, price_now) VALUES (312, 'CRPG3', 94.69);
INSERT INTO public.price (id, ticker, price_now) VALUES (167, 'PEAB3', 62);
INSERT INTO public.price (id, ticker, price_now) VALUES (209, 'SAPR4', 3.88);
INSERT INTO public.price (id, ticker, price_now) VALUES (241, 'CIEL3', 2.27);
INSERT INTO public.price (id, ticker, price_now) VALUES (244, 'BMGB4', 3.44);
INSERT INTO public.price (id, ticker, price_now) VALUES (295, 'SANB4', 16.35);
INSERT INTO public.price (id, ticker, price_now) VALUES (309, 'BRIV4', 7.51);
INSERT INTO public.price (id, ticker, price_now) VALUES (175, 'PATI4', 59);
INSERT INTO public.price (id, ticker, price_now) VALUES (304, 'EZTC3', 20.3);
INSERT INTO public.price (id, ticker, price_now) VALUES (303, 'WHRL3', 6.55);
INSERT INTO public.price (id, ticker, price_now) VALUES (305, 'REDE3', 6.51);
INSERT INTO public.price (id, ticker, price_now) VALUES (307, 'CARD3', 12.64);
INSERT INTO public.price (id, ticker, price_now) VALUES (308, 'EKTR3', 34.08);
INSERT INTO public.price (id, ticker, price_now) VALUES (261, 'CPFE3', 26.69);
INSERT INTO public.price (id, ticker, price_now) VALUES (311, 'BRIV3', 7.3);
INSERT INTO public.price (id, ticker, price_now) VALUES (313, 'CRFB3', 15.21);
INSERT INTO public.price (id, ticker, price_now) VALUES (192, 'CMIN3', 6.52);
INSERT INTO public.price (id, ticker, price_now) VALUES (173, 'DEXP4', 9.4);
INSERT INTO public.price (id, ticker, price_now) VALUES (170, 'RAPT4', 10.69);
INSERT INTO public.price (id, ticker, price_now) VALUES (176, 'TRPL4', 24.25);
INSERT INTO public.price (id, ticker, price_now) VALUES (174, 'ALLD3', 15.75);
INSERT INTO public.price (id, ticker, price_now) VALUES (179, 'DEXP3', 10.94);
INSERT INTO public.price (id, ticker, price_now) VALUES (180, 'BRSR6', 9.6);
INSERT INTO public.price (id, ticker, price_now) VALUES (181, 'JBSS3', 37.89);
INSERT INTO public.price (id, ticker, price_now) VALUES (184, 'ENAT3', 13.4);
INSERT INTO public.price (id, ticker, price_now) VALUES (332, 'PDTC3', 6.81);
INSERT INTO public.price (id, ticker, price_now) VALUES (334, 'GRND3', 8.42);
INSERT INTO public.price (id, ticker, price_now) VALUES (324, 'KLBN3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (325, 'KEPL3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (327, 'UCAS3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (328, 'LOGN3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (329, 'BTTL3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (330, 'DIRR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (337, 'GFSA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (338, 'PRNR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (333, 'SIMH3', 11.51);
INSERT INTO public.price (id, ticker, price_now) VALUES (335, 'BPAC11', 20.86);
INSERT INTO public.price (id, ticker, price_now) VALUES (336, 'TIMS3', 12.76);
INSERT INTO public.price (id, ticker, price_now) VALUES (356, 'EVEN3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (357, 'WLMM3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (362, 'TECN3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (364, 'WLMM4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (339, 'BSLI4', 16.65);
INSERT INTO public.price (id, ticker, price_now) VALUES (340, 'EQPA3', 5.08);
INSERT INTO public.price (id, ticker, price_now) VALUES (373, 'ELET5', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (341, 'BBSE3', 20.79);
INSERT INTO public.price (id, ticker, price_now) VALUES (342, 'SMTO3', 34.35);
INSERT INTO public.price (id, ticker, price_now) VALUES (398, 'PTNT3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (400, 'PGMN3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (343, 'JALL3', 9.84);
INSERT INTO public.price (id, ticker, price_now) VALUES (406, 'MTRE3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (410, 'BMIN4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (413, 'RDNI3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (414, 'MILS3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (345, 'PARD3', 18.94);
INSERT INTO public.price (id, ticker, price_now) VALUES (425, 'SBFG3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (432, 'LIPR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (433, 'STBP3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (434, 'CSED3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (436, 'BMIN3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (348, 'TUPY3', 20.61);
INSERT INTO public.price (id, ticker, price_now) VALUES (444, 'BRML3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (445, 'SOMA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (448, 'BRFS3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (453, 'DMVF3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (349, 'ENGI3', 14.54);
INSERT INTO public.price (id, ticker, price_now) VALUES (457, 'CVCB3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (460, 'AALR3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (461, 'RAIL3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (463, 'NTCO3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (466, 'SYNE3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (468, 'ANIM3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (471, 'SQIA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (397, 'WSON33', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (347, 'SOJA3', 15.8);
INSERT INTO public.price (id, ticker, price_now) VALUES (351, 'AESB3', 10.95);
INSERT INTO public.price (id, ticker, price_now) VALUES (352, 'EGIE3', 38.8);
INSERT INTO public.price (id, ticker, price_now) VALUES (353, 'OFSA3', 24.61);
INSERT INTO public.price (id, ticker, price_now) VALUES (355, 'LCAM3', 24.04);
INSERT INTO public.price (id, ticker, price_now) VALUES (359, 'SOND5', 36.01);
INSERT INTO public.price (id, ticker, price_now) VALUES (358, 'HYPE3', 29.05);
INSERT INTO public.price (id, ticker, price_now) VALUES (360, 'CXSE3', 8.15);
INSERT INTO public.price (id, ticker, price_now) VALUES (363, 'CAMB3', 4.89);
INSERT INTO public.price (id, ticker, price_now) VALUES (365, 'CPLE5', 28.51);
INSERT INTO public.price (id, ticker, price_now) VALUES (366, 'BRPR3', 7.25);
INSERT INTO public.price (id, ticker, price_now) VALUES (367, 'B3SA3', 11.16);
INSERT INTO public.price (id, ticker, price_now) VALUES (369, 'ENMT4', 80.56);
INSERT INTO public.price (id, ticker, price_now) VALUES (370, 'MRSA3B', 38.7);
INSERT INTO public.price (id, ticker, price_now) VALUES (372, 'PRIO3', 20.05);
INSERT INTO public.price (id, ticker, price_now) VALUES (361, 'FLRY3', 17.76);
INSERT INTO public.price (id, ticker, price_now) VALUES (374, 'ABEV3', 15.52);
INSERT INTO public.price (id, ticker, price_now) VALUES (407, 'BAUH4', 82.89);
INSERT INTO public.price (id, ticker, price_now) VALUES (375, 'MELK3', 3.99);
INSERT INTO public.price (id, ticker, price_now) VALUES (378, 'EQPA7', 6.7);
INSERT INTO public.price (id, ticker, price_now) VALUES (376, 'LAME3', 5.87);
INSERT INTO public.price (id, ticker, price_now) VALUES (377, 'LAME4', 5.85);
INSERT INTO public.price (id, ticker, price_now) VALUES (379, 'EQPA5', 6.92);
INSERT INTO public.price (id, ticker, price_now) VALUES (380, 'MDIA3', 25.24);
INSERT INTO public.price (id, ticker, price_now) VALUES (381, 'BSLI3', 26.02);
INSERT INTO public.price (id, ticker, price_now) VALUES (385, 'ODPV3', 12.51);
INSERT INTO public.price (id, ticker, price_now) VALUES (383, 'GPAR3', 43);
INSERT INTO public.price (id, ticker, price_now) VALUES (386, 'GMAT3', 6.06);
INSERT INTO public.price (id, ticker, price_now) VALUES (387, 'VIVT3', 49.57);
INSERT INTO public.price (id, ticker, price_now) VALUES (426, 'SULA11', 25.76);
INSERT INTO public.price (id, ticker, price_now) VALUES (388, 'AGXY3', 10.35);
INSERT INTO public.price (id, ticker, price_now) VALUES (389, 'BALM4', 12.75);
INSERT INTO public.price (id, ticker, price_now) VALUES (390, 'MRSA5B', 45.43);
INSERT INTO public.price (id, ticker, price_now) VALUES (392, 'INTB3', 27.51);
INSERT INTO public.price (id, ticker, price_now) VALUES (394, 'UGPA3', 14.61);
INSERT INTO public.price (id, ticker, price_now) VALUES (393, 'BMOB3', 14.88);
INSERT INTO public.price (id, ticker, price_now) VALUES (395, 'BLAU3', 35.4);
INSERT INTO public.price (id, ticker, price_now) VALUES (396, 'BPAN4', 10.53);
INSERT INTO public.price (id, ticker, price_now) VALUES (399, 'JOPA3', 28.6);
INSERT INTO public.price (id, ticker, price_now) VALUES (403, 'RENT3', 53.55);
INSERT INTO public.price (id, ticker, price_now) VALUES (404, 'BRGE12', 6);
INSERT INTO public.price (id, ticker, price_now) VALUES (405, 'BPAC3', 12.87);
INSERT INTO public.price (id, ticker, price_now) VALUES (409, 'RAIZ4', 6.05);
INSERT INTO public.price (id, ticker, price_now) VALUES (382, 'IGTA3', 33.13);
INSERT INTO public.price (id, ticker, price_now) VALUES (408, 'VIVA3', 24.72);
INSERT INTO public.price (id, ticker, price_now) VALUES (411, 'RPAD6', 4.35);
INSERT INTO public.price (id, ticker, price_now) VALUES (412, 'POWE3', 10.8);
INSERT INTO public.price (id, ticker, price_now) VALUES (416, 'PNVL3', 12.7);
INSERT INTO public.price (id, ticker, price_now) VALUES (417, 'JOPA4', 35);
INSERT INTO public.price (id, ticker, price_now) VALUES (418, 'BOAS3', 6.25);
INSERT INTO public.price (id, ticker, price_now) VALUES (419, 'BMKS3', 230);
INSERT INTO public.price (id, ticker, price_now) VALUES (421, 'BRGE11', 7.91);
INSERT INTO public.price (id, ticker, price_now) VALUES (422, 'BRGE3', 7.3);
INSERT INTO public.price (id, ticker, price_now) VALUES (423, 'SULA4', 8.37);
INSERT INTO public.price (id, ticker, price_now) VALUES (424, 'RPAD3', 5.97);
INSERT INTO public.price (id, ticker, price_now) VALUES (401, 'JPSA3', 29.02);
INSERT INTO public.price (id, ticker, price_now) VALUES (427, 'LUXM4', 81.95);
INSERT INTO public.price (id, ticker, price_now) VALUES (428, 'SULA3', 8.97);
INSERT INTO public.price (id, ticker, price_now) VALUES (429, 'AFLT3', 8.54);
INSERT INTO public.price (id, ticker, price_now) VALUES (430, 'TFCO4', 12.56);
INSERT INTO public.price (id, ticker, price_now) VALUES (319, 'COCE3', 58.92);
INSERT INTO public.price (id, ticker, price_now) VALUES (320, 'CGAS5', 150);
INSERT INTO public.price (id, ticker, price_now) VALUES (431, 'IGTI3', 2.83);
INSERT INTO public.price (id, ticker, price_now) VALUES (321, 'ASAI3', 13.1);
INSERT INTO public.price (id, ticker, price_now) VALUES (459, 'YDUQ3', 20.86);
INSERT INTO public.price (id, ticker, price_now) VALUES (462, 'MGLU3', 6.83);
INSERT INTO public.price (id, ticker, price_now) VALUES (465, 'RDOR3', 45.84);
INSERT INTO public.price (id, ticker, price_now) VALUES (467, 'AERI3', 6.71);
INSERT INTO public.price (id, ticker, price_now) VALUES (449, 'RPAD5', 7.22);
INSERT INTO public.price (id, ticker, price_now) VALUES (443, 'VAMO3', 11.82);
INSERT INTO public.price (id, ticker, price_now) VALUES (415, 'ARZZ3', 75.1);
INSERT INTO public.price (id, ticker, price_now) VALUES (435, 'IGTI11', 18.77);
INSERT INTO public.price (id, ticker, price_now) VALUES (437, 'MULT3', 19.18);
INSERT INTO public.price (id, ticker, price_now) VALUES (439, 'NGRD3', 2.64);
INSERT INTO public.price (id, ticker, price_now) VALUES (440, 'AMBP3', 40.88);
INSERT INTO public.price (id, ticker, price_now) VALUES (441, 'CCRO3', 11.78);
INSERT INTO public.price (id, ticker, price_now) VALUES (442, 'ALSO3', 21.2);
INSERT INTO public.price (id, ticker, price_now) VALUES (464, 'MERC4', 10.57);
INSERT INTO public.price (id, ticker, price_now) VALUES (446, 'MOSI3', 8.4);
INSERT INTO public.price (id, ticker, price_now) VALUES (447, 'CEGR3', 60);
INSERT INTO public.price (id, ticker, price_now) VALUES (470, 'PETZ3', 16.63);
INSERT INTO public.price (id, ticker, price_now) VALUES (469, 'HAPV3', 10.59);
INSERT INTO public.price (id, ticker, price_now) VALUES (346, 'BMEB3', 12.5);
INSERT INTO public.price (id, ticker, price_now) VALUES (450, 'WEGE3', 33.29);
INSERT INTO public.price (id, ticker, price_now) VALUES (451, 'SCAR3', 39);
INSERT INTO public.price (id, ticker, price_now) VALUES (454, 'RADL3', 23.71);
INSERT INTO public.price (id, ticker, price_now) VALUES (452, 'ALPA3', 31.2);
INSERT INTO public.price (id, ticker, price_now) VALUES (317, 'SBSP3', 40.04);
INSERT INTO public.price (id, ticker, price_now) VALUES (318, 'FESA3', 60);
INSERT INTO public.price (id, ticker, price_now) VALUES (455, 'ALPA4', 36.75);
INSERT INTO public.price (id, ticker, price_now) VALUES (458, 'TOTS3', 28.32);
INSERT INTO public.price (id, ticker, price_now) VALUES (322, 'CSAB4', 42.75);
INSERT INTO public.price (id, ticker, price_now) VALUES (323, 'PSSA3', 20.88);
INSERT INTO public.price (id, ticker, price_now) VALUES (326, 'AURA33', 45.35);
INSERT INTO public.price (id, ticker, price_now) VALUES (331, 'WHRL4', 7.85);
INSERT INTO public.price (id, ticker, price_now) VALUES (472, 'CBEE3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (475, 'BIDI3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (477, 'BIDI4', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (478, 'SEQL3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (479, 'VIIA3', 0);
INSERT INTO public.price (id, ticker, price_now) VALUES (14, 'OMGE3', 27.57);
INSERT INTO public.price (id, ticker, price_now) VALUES (87, 'BRBI11', 14.94);
INSERT INTO public.price (id, ticker, price_now) VALUES (111, 'VVEO3', 19);
INSERT INTO public.price (id, ticker, price_now) VALUES (136, 'CLSC3', 62.9);
INSERT INTO public.price (id, ticker, price_now) VALUES (152, 'PEAB4', 71);
INSERT INTO public.price (id, ticker, price_now) VALUES (166, 'PCAR3', 22.58);
INSERT INTO public.price (id, ticker, price_now) VALUES (168, 'BGIP4', 24.45);
INSERT INTO public.price (id, ticker, price_now) VALUES (169, 'EUCA3', 12.73);
INSERT INTO public.price (id, ticker, price_now) VALUES (187, 'BNBR3', 72.94);
INSERT INTO public.price (id, ticker, price_now) VALUES (203, 'BRSR3', 11.67);
INSERT INTO public.price (id, ticker, price_now) VALUES (213, 'UNIP6', 99.61);
INSERT INTO public.price (id, ticker, price_now) VALUES (218, 'UNIP3', 98.02);
INSERT INTO public.price (id, ticker, price_now) VALUES (243, 'EQTL3', 22.82);
INSERT INTO public.price (id, ticker, price_now) VALUES (259, 'ITSA3', 9.37);
INSERT INTO public.price (id, ticker, price_now) VALUES (274, 'EMAE4', 71.3);
INSERT INTO public.price (id, ticker, price_now) VALUES (293, 'CRIV4', 5.58);
INSERT INTO public.price (id, ticker, price_now) VALUES (310, 'COCE5', 56.84);
INSERT INTO public.price (id, ticker, price_now) VALUES (315, 'DOHL3', 19);
INSERT INTO public.price (id, ticker, price_now) VALUES (316, 'CGAS3', 140);
INSERT INTO public.price (id, ticker, price_now) VALUES (344, 'QUAL3', 16.82);
INSERT INTO public.price (id, ticker, price_now) VALUES (350, 'TEND3', 16.77);
INSERT INTO public.price (id, ticker, price_now) VALUES (354, 'ENEV3', 14.19);
INSERT INTO public.price (id, ticker, price_now) VALUES (368, 'ENMT3', 77.49);
INSERT INTO public.price (id, ticker, price_now) VALUES (384, 'VITT3', 13.75);
INSERT INTO public.price (id, ticker, price_now) VALUES (402, 'BALM3', 15.65);
INSERT INTO public.price (id, ticker, price_now) VALUES (420, 'LJQQ3', 11.38);
INSERT INTO public.price (id, ticker, price_now) VALUES (438, 'BRGE8', 9.65);
INSERT INTO public.price (id, ticker, price_now) VALUES (456, 'LREN3', 24.46);
INSERT INTO public.price (id, ticker, price_now) VALUES (473, 'MERC3', 25);
INSERT INTO public.price (id, ticker, price_now) VALUES (474, 'AMER3', 31.03);
INSERT INTO public.price (id, ticker, price_now) VALUES (476, 'BIDI11', 29);
INSERT INTO public.price (id, ticker, price_now) VALUES (480, 'LWSA3', 12.9);


--
-- Data for Name: stock; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.stock (id, ticker) VALUES (1, 'GNDI3');
INSERT INTO public.stock (id, ticker) VALUES (2, 'APER3');
INSERT INTO public.stock (id, ticker) VALUES (3, 'CASH3');
INSERT INTO public.stock (id, ticker) VALUES (4, 'RCSL3');
INSERT INTO public.stock (id, ticker) VALUES (5, 'DASA3');
INSERT INTO public.stock (id, ticker) VALUES (6, 'TCNO3');
INSERT INTO public.stock (id, ticker) VALUES (7, 'MAPT4');
INSERT INTO public.stock (id, ticker) VALUES (8, 'RCSL4');
INSERT INTO public.stock (id, ticker) VALUES (9, 'TCNO4');
INSERT INTO public.stock (id, ticker) VALUES (10, 'NORD3');
INSERT INTO public.stock (id, ticker) VALUES (11, 'FRTA3');
INSERT INTO public.stock (id, ticker) VALUES (12, 'EMBR3');
INSERT INTO public.stock (id, ticker) VALUES (13, 'ELMD3');
INSERT INTO public.stock (id, ticker) VALUES (14, 'OMGE3');
INSERT INTO public.stock (id, ticker) VALUES (15, 'RRRP3');
INSERT INTO public.stock (id, ticker) VALUES (16, 'VLID3');
INSERT INTO public.stock (id, ticker) VALUES (17, 'ORVR3');
INSERT INTO public.stock (id, ticker) VALUES (18, 'TXRX3');
INSERT INTO public.stock (id, ticker) VALUES (19, 'ECOR3');
INSERT INTO public.stock (id, ticker) VALUES (20, 'TELB3');
INSERT INTO public.stock (id, ticker) VALUES (21, 'HBSA3');
INSERT INTO public.stock (id, ticker) VALUES (22, 'DTCY3');
INSERT INTO public.stock (id, ticker) VALUES (23, 'HBRE3');
INSERT INTO public.stock (id, ticker) VALUES (24, 'SMFT3');
INSERT INTO public.stock (id, ticker) VALUES (25, 'WEST3');
INSERT INTO public.stock (id, ticker) VALUES (26, 'FRIO3');
INSERT INTO public.stock (id, ticker) VALUES (27, 'BIOM3');
INSERT INTO public.stock (id, ticker) VALUES (28, 'MEAL3');
INSERT INTO public.stock (id, ticker) VALUES (29, 'AMAR3');
INSERT INTO public.stock (id, ticker) VALUES (30, 'MSPA3');
INSERT INTO public.stock (id, ticker) VALUES (31, 'OPCT3');
INSERT INTO public.stock (id, ticker) VALUES (32, 'MSPA4');
INSERT INTO public.stock (id, ticker) VALUES (33, 'TELB4');
INSERT INTO public.stock (id, ticker) VALUES (34, 'BLUT3');
INSERT INTO public.stock (id, ticker) VALUES (35, 'TXRX4');
INSERT INTO public.stock (id, ticker) VALUES (36, 'ENJU3');
INSERT INTO public.stock (id, ticker) VALUES (37, 'MBLY3');
INSERT INTO public.stock (id, ticker) VALUES (38, 'IRBR3');
INSERT INTO public.stock (id, ticker) VALUES (39, 'BAHI3');
INSERT INTO public.stock (id, ticker) VALUES (40, 'PINE4');
INSERT INTO public.stock (id, ticker) VALUES (41, 'ALPK3');
INSERT INTO public.stock (id, ticker) VALUES (42, 'CTNM3');
INSERT INTO public.stock (id, ticker) VALUES (43, 'BKBR3');
INSERT INTO public.stock (id, ticker) VALUES (44, 'ADHM3');
INSERT INTO public.stock (id, ticker) VALUES (45, 'AHEB3');
INSERT INTO public.stock (id, ticker) VALUES (46, 'AHEB5');
INSERT INTO public.stock (id, ticker) VALUES (47, 'CEED3');
INSERT INTO public.stock (id, ticker) VALUES (48, 'ESTR4');
INSERT INTO public.stock (id, ticker) VALUES (49, 'BLUT4');
INSERT INTO public.stock (id, ticker) VALUES (50, 'CRDE3');
INSERT INTO public.stock (id, ticker) VALUES (51, 'SGPS3');
INSERT INTO public.stock (id, ticker) VALUES (52, 'VIVR3');
INSERT INTO public.stock (id, ticker) VALUES (53, 'SHOW3');
INSERT INTO public.stock (id, ticker) VALUES (54, 'AZUL4');
INSERT INTO public.stock (id, ticker) VALUES (55, 'CTNM4');
INSERT INTO public.stock (id, ticker) VALUES (56, 'OIBR4');
INSERT INTO public.stock (id, ticker) VALUES (57, 'TCSA3');
INSERT INTO public.stock (id, ticker) VALUES (58, 'BAHI11');
INSERT INTO public.stock (id, ticker) VALUES (59, 'GOLL4');
INSERT INTO public.stock (id, ticker) VALUES (60, 'PLAS3');
INSERT INTO public.stock (id, ticker) VALUES (61, 'OIBR3');
INSERT INTO public.stock (id, ticker) VALUES (62, 'HOOT4');
INSERT INTO public.stock (id, ticker) VALUES (63, 'GSHP3');
INSERT INTO public.stock (id, ticker) VALUES (64, 'COGN3');
INSERT INTO public.stock (id, ticker) VALUES (65, 'PMAM3');
INSERT INTO public.stock (id, ticker) VALUES (66, 'ATMP3');
INSERT INTO public.stock (id, ticker) VALUES (67, 'AVLL3');
INSERT INTO public.stock (id, ticker) VALUES (68, 'RPMG3');
INSERT INTO public.stock (id, ticker) VALUES (69, 'MTIG4');
INSERT INTO public.stock (id, ticker) VALUES (70, 'INEP3');
INSERT INTO public.stock (id, ticker) VALUES (71, 'INEP4');
INSERT INTO public.stock (id, ticker) VALUES (72, 'BBRK3');
INSERT INTO public.stock (id, ticker) VALUES (73, 'JFEN3');
INSERT INTO public.stock (id, ticker) VALUES (74, 'IGBR3');
INSERT INTO public.stock (id, ticker) VALUES (75, 'BDLL3');
INSERT INTO public.stock (id, ticker) VALUES (76, 'BDLL4');
INSERT INTO public.stock (id, ticker) VALUES (77, 'SNSY5');
INSERT INTO public.stock (id, ticker) VALUES (78, 'SLED3');
INSERT INTO public.stock (id, ticker) VALUES (79, 'PDGR3');
INSERT INTO public.stock (id, ticker) VALUES (80, 'TEKA3');
INSERT INTO public.stock (id, ticker) VALUES (81, 'SLED4');
INSERT INTO public.stock (id, ticker) VALUES (82, 'OSXB3');
INSERT INTO public.stock (id, ticker) VALUES (83, 'LLIS3');
INSERT INTO public.stock (id, ticker) VALUES (84, 'TEKA4');
INSERT INTO public.stock (id, ticker) VALUES (85, 'HETA4');
INSERT INTO public.stock (id, ticker) VALUES (86, 'ARML3');
INSERT INTO public.stock (id, ticker) VALUES (87, 'BRBI11');
INSERT INTO public.stock (id, ticker) VALUES (88, 'BRIT3');
INSERT INTO public.stock (id, ticker) VALUES (89, 'CBAV3');
INSERT INTO public.stock (id, ticker) VALUES (90, 'CLSA3');
INSERT INTO public.stock (id, ticker) VALUES (91, 'DESK3');
INSERT INTO public.stock (id, ticker) VALUES (92, 'DOTZ3');
INSERT INTO public.stock (id, ticker) VALUES (93, 'FIQE3');
INSERT INTO public.stock (id, ticker) VALUES (94, 'GETT3');
INSERT INTO public.stock (id, ticker) VALUES (95, 'GETT4');
INSERT INTO public.stock (id, ticker) VALUES (96, 'GGPS3');
INSERT INTO public.stock (id, ticker) VALUES (97, 'IFCM3');
INSERT INTO public.stock (id, ticker) VALUES (98, 'KRSA3');
INSERT INTO public.stock (id, ticker) VALUES (99, 'LVTC3');
INSERT INTO public.stock (id, ticker) VALUES (100, 'MATD3');
INSERT INTO public.stock (id, ticker) VALUES (101, 'MLAS3');
INSERT INTO public.stock (id, ticker) VALUES (102, 'MODL11');
INSERT INTO public.stock (id, ticker) VALUES (103, 'MODL3');
INSERT INTO public.stock (id, ticker) VALUES (104, 'MODL4');
INSERT INTO public.stock (id, ticker) VALUES (105, 'NINJ3');
INSERT INTO public.stock (id, ticker) VALUES (106, 'ONCO3');
INSERT INTO public.stock (id, ticker) VALUES (107, 'PORT3');
INSERT INTO public.stock (id, ticker) VALUES (108, 'RECV3');
INSERT INTO public.stock (id, ticker) VALUES (109, 'TRAD3');
INSERT INTO public.stock (id, ticker) VALUES (110, 'TTEN3');
INSERT INTO public.stock (id, ticker) VALUES (111, 'VVEO3');
INSERT INTO public.stock (id, ticker) VALUES (112, 'MWET4');
INSERT INTO public.stock (id, ticker) VALUES (113, 'MWET3');
INSERT INTO public.stock (id, ticker) VALUES (114, 'MGEL4');
INSERT INTO public.stock (id, ticker) VALUES (115, 'CEBR5');
INSERT INTO public.stock (id, ticker) VALUES (116, 'CEBR6');
INSERT INTO public.stock (id, ticker) VALUES (117, 'CEBR3');
INSERT INTO public.stock (id, ticker) VALUES (118, 'RSID3');
INSERT INTO public.stock (id, ticker) VALUES (119, 'GPIV33');
INSERT INTO public.stock (id, ticker) VALUES (120, 'TPIS3');
INSERT INTO public.stock (id, ticker) VALUES (121, 'DMMO3');
INSERT INTO public.stock (id, ticker) VALUES (122, 'LUPA3');
INSERT INTO public.stock (id, ticker) VALUES (123, 'CTKA4');
INSERT INTO public.stock (id, ticker) VALUES (124, 'AZEV4');
INSERT INTO public.stock (id, ticker) VALUES (125, 'BRKM6');
INSERT INTO public.stock (id, ticker) VALUES (126, 'HBTS5');
INSERT INTO public.stock (id, ticker) VALUES (127, 'AZEV3');
INSERT INTO public.stock (id, ticker) VALUES (128, 'USIM3');
INSERT INTO public.stock (id, ticker) VALUES (129, 'BAZA3');
INSERT INTO public.stock (id, ticker) VALUES (130, 'CSNA3');
INSERT INTO public.stock (id, ticker) VALUES (131, 'USIM5');
INSERT INTO public.stock (id, ticker) VALUES (132, 'RNEW4');
INSERT INTO public.stock (id, ticker) VALUES (133, 'RNEW11');
INSERT INTO public.stock (id, ticker) VALUES (134, 'HAGA4');
INSERT INTO public.stock (id, ticker) VALUES (135, 'RNEW3');
INSERT INTO public.stock (id, ticker) VALUES (136, 'CLSC3');
INSERT INTO public.stock (id, ticker) VALUES (137, 'EUCA4');
INSERT INTO public.stock (id, ticker) VALUES (138, 'CTKA3');
INSERT INTO public.stock (id, ticker) VALUES (139, 'GOAU3');
INSERT INTO public.stock (id, ticker) VALUES (140, 'MNDL3');
INSERT INTO public.stock (id, ticker) VALUES (141, 'CPLE3');
INSERT INTO public.stock (id, ticker) VALUES (142, 'PETR4');
INSERT INTO public.stock (id, ticker) VALUES (143, 'USIM6');
INSERT INTO public.stock (id, ticker) VALUES (144, 'PETR3');
INSERT INTO public.stock (id, ticker) VALUES (145, 'CPLE11');
INSERT INTO public.stock (id, ticker) VALUES (146, 'MRFG3');
INSERT INTO public.stock (id, ticker) VALUES (147, 'GGBR3');
INSERT INTO public.stock (id, ticker) VALUES (148, 'CPLE6');
INSERT INTO public.stock (id, ticker) VALUES (149, 'TKNO4');
INSERT INTO public.stock (id, ticker) VALUES (150, 'GOAU4');
INSERT INTO public.stock (id, ticker) VALUES (151, 'ETER3');
INSERT INTO public.stock (id, ticker) VALUES (152, 'PEAB4');
INSERT INTO public.stock (id, ticker) VALUES (153, 'BRKM3');
INSERT INTO public.stock (id, ticker) VALUES (154, 'CLSC4');
INSERT INTO public.stock (id, ticker) VALUES (155, 'BRKM5');
INSERT INTO public.stock (id, ticker) VALUES (156, 'DOHL4');
INSERT INTO public.stock (id, ticker) VALUES (157, 'CESP3');
INSERT INTO public.stock (id, ticker) VALUES (158, 'FHER3');
INSERT INTO public.stock (id, ticker) VALUES (159, 'BOBR4');
INSERT INTO public.stock (id, ticker) VALUES (160, 'BRAP3');
INSERT INTO public.stock (id, ticker) VALUES (161, 'CESP6');
INSERT INTO public.stock (id, ticker) VALUES (162, 'TASA4');
INSERT INTO public.stock (id, ticker) VALUES (163, 'GGBR4');
INSERT INTO public.stock (id, ticker) VALUES (164, 'TASA3');
INSERT INTO public.stock (id, ticker) VALUES (165, 'BRAP4');
INSERT INTO public.stock (id, ticker) VALUES (166, 'PCAR3');
INSERT INTO public.stock (id, ticker) VALUES (167, 'PEAB3');
INSERT INTO public.stock (id, ticker) VALUES (168, 'BGIP4');
INSERT INTO public.stock (id, ticker) VALUES (169, 'EUCA3');
INSERT INTO public.stock (id, ticker) VALUES (170, 'RAPT4');
INSERT INTO public.stock (id, ticker) VALUES (171, 'VALE3');
INSERT INTO public.stock (id, ticker) VALUES (172, 'JHSF3');
INSERT INTO public.stock (id, ticker) VALUES (173, 'DEXP4');
INSERT INTO public.stock (id, ticker) VALUES (174, 'ALLD3');
INSERT INTO public.stock (id, ticker) VALUES (175, 'PATI4');
INSERT INTO public.stock (id, ticker) VALUES (176, 'TRPL4');
INSERT INTO public.stock (id, ticker) VALUES (177, 'RAPT3');
INSERT INTO public.stock (id, ticker) VALUES (178, 'EPAR3');
INSERT INTO public.stock (id, ticker) VALUES (179, 'DEXP3');
INSERT INTO public.stock (id, ticker) VALUES (180, 'BRSR6');
INSERT INTO public.stock (id, ticker) VALUES (181, 'JBSS3');
INSERT INTO public.stock (id, ticker) VALUES (182, 'EALT4');
INSERT INTO public.stock (id, ticker) VALUES (183, 'CEDO4');
INSERT INTO public.stock (id, ticker) VALUES (184, 'ENAT3');
INSERT INTO public.stock (id, ticker) VALUES (185, 'CEPE5');
INSERT INTO public.stock (id, ticker) VALUES (186, 'CTSA4');
INSERT INTO public.stock (id, ticker) VALUES (187, 'BNBR3');
INSERT INTO public.stock (id, ticker) VALUES (188, 'POSI3');
INSERT INTO public.stock (id, ticker) VALUES (189, 'CGRA4');
INSERT INTO public.stock (id, ticker) VALUES (190, 'CGRA3');
INSERT INTO public.stock (id, ticker) VALUES (191, 'ROMI3');
INSERT INTO public.stock (id, ticker) VALUES (192, 'CMIN3');
INSERT INTO public.stock (id, ticker) VALUES (193, 'TAEE11');
INSERT INTO public.stock (id, ticker) VALUES (194, 'TAEE4');
INSERT INTO public.stock (id, ticker) VALUES (195, 'TAEE3');
INSERT INTO public.stock (id, ticker) VALUES (196, 'PATI3');
INSERT INTO public.stock (id, ticker) VALUES (197, 'LAVV3');
INSERT INTO public.stock (id, ticker) VALUES (198, 'ALUP3');
INSERT INTO public.stock (id, ticker) VALUES (199, 'SAPR3');
INSERT INTO public.stock (id, ticker) VALUES (200, 'NEOE3');
INSERT INTO public.stock (id, ticker) VALUES (201, 'ALUP11');
INSERT INTO public.stock (id, ticker) VALUES (202, 'POMO3');
INSERT INTO public.stock (id, ticker) VALUES (203, 'BRSR3');
INSERT INTO public.stock (id, ticker) VALUES (204, 'ALUP4');
INSERT INTO public.stock (id, ticker) VALUES (205, 'CEPE6');
INSERT INTO public.stock (id, ticker) VALUES (206, 'BGIP3');
INSERT INTO public.stock (id, ticker) VALUES (207, 'SAPR11');
INSERT INTO public.stock (id, ticker) VALUES (208, 'CESP5');
INSERT INTO public.stock (id, ticker) VALUES (209, 'SAPR4');
INSERT INTO public.stock (id, ticker) VALUES (210, 'BBAS3');
INSERT INTO public.stock (id, ticker) VALUES (211, 'UNIP5');
INSERT INTO public.stock (id, ticker) VALUES (212, 'BMEB4');
INSERT INTO public.stock (id, ticker) VALUES (213, 'UNIP6');
INSERT INTO public.stock (id, ticker) VALUES (214, 'VBBR3');
INSERT INTO public.stock (id, ticker) VALUES (215, 'CSRN5');
INSERT INTO public.stock (id, ticker) VALUES (216, 'ENGI4');
INSERT INTO public.stock (id, ticker) VALUES (217, 'CEEB3');
INSERT INTO public.stock (id, ticker) VALUES (218, 'UNIP3');
INSERT INTO public.stock (id, ticker) VALUES (219, 'TRPL3');
INSERT INTO public.stock (id, ticker) VALUES (220, 'CMIG4');
INSERT INTO public.stock (id, ticker) VALUES (221, 'MDNE3');
INSERT INTO public.stock (id, ticker) VALUES (222, 'HBOR3');
INSERT INTO public.stock (id, ticker) VALUES (223, 'PTNT4');
INSERT INTO public.stock (id, ticker) VALUES (224, 'MNPR3');
INSERT INTO public.stock (id, ticker) VALUES (225, 'CSRN3');
INSERT INTO public.stock (id, ticker) VALUES (226, 'CEDO3');
INSERT INTO public.stock (id, ticker) VALUES (227, 'POMO4');
INSERT INTO public.stock (id, ticker) VALUES (228, 'LIGT3');
INSERT INTO public.stock (id, ticker) VALUES (229, 'ENBR3');
INSERT INTO public.stock (id, ticker) VALUES (230, 'HAGA3');
INSERT INTO public.stock (id, ticker) VALUES (231, 'CYRE3');
INSERT INTO public.stock (id, ticker) VALUES (232, 'PLPL3');
INSERT INTO public.stock (id, ticker) VALUES (233, 'GEPA3');
INSERT INTO public.stock (id, ticker) VALUES (234, 'GEPA4');
INSERT INTO public.stock (id, ticker) VALUES (235, 'EKTR4');
INSERT INTO public.stock (id, ticker) VALUES (236, 'BEES3');
INSERT INTO public.stock (id, ticker) VALUES (237, 'CRPG6');
INSERT INTO public.stock (id, ticker) VALUES (238, 'CTSA3');
INSERT INTO public.stock (id, ticker) VALUES (239, 'SUZB3');
INSERT INTO public.stock (id, ticker) VALUES (240, 'PFRM3');
INSERT INTO public.stock (id, ticker) VALUES (241, 'CIEL3');
INSERT INTO public.stock (id, ticker) VALUES (242, 'LPSB3');
INSERT INTO public.stock (id, ticker) VALUES (243, 'EQTL3');
INSERT INTO public.stock (id, ticker) VALUES (244, 'BMGB4');
INSERT INTO public.stock (id, ticker) VALUES (245, 'TRIS3');
INSERT INTO public.stock (id, ticker) VALUES (246, 'CSRN6');
INSERT INTO public.stock (id, ticker) VALUES (247, 'AGRO3');
INSERT INTO public.stock (id, ticker) VALUES (248, 'SLCE3');
INSERT INTO public.stock (id, ticker) VALUES (249, 'CSMG3');
INSERT INTO public.stock (id, ticker) VALUES (250, 'CEAB3');
INSERT INTO public.stock (id, ticker) VALUES (251, 'CRPG5');
INSERT INTO public.stock (id, ticker) VALUES (252, 'PTBL3');
INSERT INTO public.stock (id, ticker) VALUES (253, 'ENGI11');
INSERT INTO public.stock (id, ticker) VALUES (254, 'LEVE3');
INSERT INTO public.stock (id, ticker) VALUES (255, 'WIZS3');
INSERT INTO public.stock (id, ticker) VALUES (256, 'MTSA4');
INSERT INTO public.stock (id, ticker) VALUES (257, 'ITSA4');
INSERT INTO public.stock (id, ticker) VALUES (258, 'RANI3');
INSERT INTO public.stock (id, ticker) VALUES (259, 'ITSA3');
INSERT INTO public.stock (id, ticker) VALUES (260, 'BBDC3');
INSERT INTO public.stock (id, ticker) VALUES (261, 'CPFE3');
INSERT INTO public.stock (id, ticker) VALUES (262, 'CMIG3');
INSERT INTO public.stock (id, ticker) VALUES (263, 'CRIV3');
INSERT INTO public.stock (id, ticker) VALUES (264, 'ESPA3');
INSERT INTO public.stock (id, ticker) VALUES (265, 'MYPK3');
INSERT INTO public.stock (id, ticker) VALUES (266, 'LOGG3');
INSERT INTO public.stock (id, ticker) VALUES (267, 'SANB3');
INSERT INTO public.stock (id, ticker) VALUES (268, 'ABCB4');
INSERT INTO public.stock (id, ticker) VALUES (269, 'BRSR5');
INSERT INTO public.stock (id, ticker) VALUES (270, 'BEES4');
INSERT INTO public.stock (id, ticker) VALUES (271, 'SHUL4');
INSERT INTO public.stock (id, ticker) VALUES (272, 'CSAN3');
INSERT INTO public.stock (id, ticker) VALUES (273, 'EEEL4');
INSERT INTO public.stock (id, ticker) VALUES (274, 'EMAE4');
INSERT INTO public.stock (id, ticker) VALUES (275, 'KLBN4');
INSERT INTO public.stock (id, ticker) VALUES (276, 'CURY3');
INSERT INTO public.stock (id, ticker) VALUES (277, 'ITUB3');
INSERT INTO public.stock (id, ticker) VALUES (278, 'ATOM3');
INSERT INTO public.stock (id, ticker) VALUES (279, 'BPAC5');
INSERT INTO public.stock (id, ticker) VALUES (280, 'SANB11');
INSERT INTO public.stock (id, ticker) VALUES (281, 'EQMA3B');
INSERT INTO public.stock (id, ticker) VALUES (282, 'KLBN11');
INSERT INTO public.stock (id, ticker) VALUES (283, 'SEER3');
INSERT INTO public.stock (id, ticker) VALUES (284, 'EEEL3');
INSERT INTO public.stock (id, ticker) VALUES (285, 'MRVE3');
INSERT INTO public.stock (id, ticker) VALUES (286, 'CAML3');
INSERT INTO public.stock (id, ticker) VALUES (287, 'BBDC4');
INSERT INTO public.stock (id, ticker) VALUES (288, 'VULC3');
INSERT INTO public.stock (id, ticker) VALUES (289, 'RSUL4');
INSERT INTO public.stock (id, ticker) VALUES (290, 'ELET6');
INSERT INTO public.stock (id, ticker) VALUES (291, 'MOAR3');
INSERT INTO public.stock (id, ticker) VALUES (292, 'EALT3');
INSERT INTO public.stock (id, ticker) VALUES (293, 'CRIV4');
INSERT INTO public.stock (id, ticker) VALUES (294, 'ITUB4');
INSERT INTO public.stock (id, ticker) VALUES (295, 'SANB4');
INSERT INTO public.stock (id, ticker) VALUES (296, 'ELET3');
INSERT INTO public.stock (id, ticker) VALUES (297, 'DXCO3');
INSERT INTO public.stock (id, ticker) VALUES (298, 'JSLG3');
INSERT INTO public.stock (id, ticker) VALUES (299, 'FESA4');
INSERT INTO public.stock (id, ticker) VALUES (300, 'FRAS3');
INSERT INTO public.stock (id, ticker) VALUES (301, 'MOVI3');
INSERT INTO public.stock (id, ticker) VALUES (302, 'TGMA3');
INSERT INTO public.stock (id, ticker) VALUES (303, 'WHRL3');
INSERT INTO public.stock (id, ticker) VALUES (304, 'EZTC3');
INSERT INTO public.stock (id, ticker) VALUES (305, 'REDE3');
INSERT INTO public.stock (id, ticker) VALUES (306, 'BEEF3');
INSERT INTO public.stock (id, ticker) VALUES (307, 'CARD3');
INSERT INTO public.stock (id, ticker) VALUES (308, 'EKTR3');
INSERT INTO public.stock (id, ticker) VALUES (309, 'BRIV4');
INSERT INTO public.stock (id, ticker) VALUES (310, 'COCE5');
INSERT INTO public.stock (id, ticker) VALUES (311, 'BRIV3');
INSERT INTO public.stock (id, ticker) VALUES (312, 'CRPG3');
INSERT INTO public.stock (id, ticker) VALUES (313, 'CRFB3');
INSERT INTO public.stock (id, ticker) VALUES (314, 'GUAR3');
INSERT INTO public.stock (id, ticker) VALUES (315, 'DOHL3');
INSERT INTO public.stock (id, ticker) VALUES (316, 'CGAS3');
INSERT INTO public.stock (id, ticker) VALUES (317, 'SBSP3');
INSERT INTO public.stock (id, ticker) VALUES (318, 'FESA3');
INSERT INTO public.stock (id, ticker) VALUES (319, 'COCE3');
INSERT INTO public.stock (id, ticker) VALUES (320, 'CGAS5');
INSERT INTO public.stock (id, ticker) VALUES (321, 'ASAI3');
INSERT INTO public.stock (id, ticker) VALUES (322, 'CSAB4');
INSERT INTO public.stock (id, ticker) VALUES (323, 'PSSA3');
INSERT INTO public.stock (id, ticker) VALUES (324, 'KLBN3');
INSERT INTO public.stock (id, ticker) VALUES (325, 'KEPL3');
INSERT INTO public.stock (id, ticker) VALUES (326, 'AURA33');
INSERT INTO public.stock (id, ticker) VALUES (327, 'UCAS3');
INSERT INTO public.stock (id, ticker) VALUES (328, 'LOGN3');
INSERT INTO public.stock (id, ticker) VALUES (329, 'BTTL3');
INSERT INTO public.stock (id, ticker) VALUES (330, 'DIRR3');
INSERT INTO public.stock (id, ticker) VALUES (331, 'WHRL4');
INSERT INTO public.stock (id, ticker) VALUES (332, 'PDTC3');
INSERT INTO public.stock (id, ticker) VALUES (333, 'SIMH3');
INSERT INTO public.stock (id, ticker) VALUES (334, 'GRND3');
INSERT INTO public.stock (id, ticker) VALUES (335, 'BPAC11');
INSERT INTO public.stock (id, ticker) VALUES (336, 'TIMS3');
INSERT INTO public.stock (id, ticker) VALUES (337, 'GFSA3');
INSERT INTO public.stock (id, ticker) VALUES (338, 'PRNR3');
INSERT INTO public.stock (id, ticker) VALUES (339, 'BSLI4');
INSERT INTO public.stock (id, ticker) VALUES (340, 'EQPA3');
INSERT INTO public.stock (id, ticker) VALUES (341, 'BBSE3');
INSERT INTO public.stock (id, ticker) VALUES (342, 'SMTO3');
INSERT INTO public.stock (id, ticker) VALUES (343, 'JALL3');
INSERT INTO public.stock (id, ticker) VALUES (344, 'QUAL3');
INSERT INTO public.stock (id, ticker) VALUES (345, 'PARD3');
INSERT INTO public.stock (id, ticker) VALUES (346, 'BMEB3');
INSERT INTO public.stock (id, ticker) VALUES (347, 'SOJA3');
INSERT INTO public.stock (id, ticker) VALUES (348, 'TUPY3');
INSERT INTO public.stock (id, ticker) VALUES (349, 'ENGI3');
INSERT INTO public.stock (id, ticker) VALUES (350, 'TEND3');
INSERT INTO public.stock (id, ticker) VALUES (351, 'AESB3');
INSERT INTO public.stock (id, ticker) VALUES (352, 'EGIE3');
INSERT INTO public.stock (id, ticker) VALUES (353, 'OFSA3');
INSERT INTO public.stock (id, ticker) VALUES (354, 'ENEV3');
INSERT INTO public.stock (id, ticker) VALUES (355, 'LCAM3');
INSERT INTO public.stock (id, ticker) VALUES (356, 'EVEN3');
INSERT INTO public.stock (id, ticker) VALUES (357, 'WLMM3');
INSERT INTO public.stock (id, ticker) VALUES (358, 'HYPE3');
INSERT INTO public.stock (id, ticker) VALUES (359, 'SOND5');
INSERT INTO public.stock (id, ticker) VALUES (360, 'CXSE3');
INSERT INTO public.stock (id, ticker) VALUES (361, 'FLRY3');
INSERT INTO public.stock (id, ticker) VALUES (362, 'TECN3');
INSERT INTO public.stock (id, ticker) VALUES (363, 'CAMB3');
INSERT INTO public.stock (id, ticker) VALUES (364, 'WLMM4');
INSERT INTO public.stock (id, ticker) VALUES (365, 'CPLE5');
INSERT INTO public.stock (id, ticker) VALUES (366, 'BRPR3');
INSERT INTO public.stock (id, ticker) VALUES (367, 'B3SA3');
INSERT INTO public.stock (id, ticker) VALUES (368, 'ENMT3');
INSERT INTO public.stock (id, ticker) VALUES (369, 'ENMT4');
INSERT INTO public.stock (id, ticker) VALUES (370, 'MRSA3B');
INSERT INTO public.stock (id, ticker) VALUES (372, 'PRIO3');
INSERT INTO public.stock (id, ticker) VALUES (373, 'ELET5');
INSERT INTO public.stock (id, ticker) VALUES (374, 'ABEV3');
INSERT INTO public.stock (id, ticker) VALUES (375, 'MELK3');
INSERT INTO public.stock (id, ticker) VALUES (376, 'LAME3');
INSERT INTO public.stock (id, ticker) VALUES (377, 'LAME4');
INSERT INTO public.stock (id, ticker) VALUES (378, 'EQPA7');
INSERT INTO public.stock (id, ticker) VALUES (379, 'EQPA5');
INSERT INTO public.stock (id, ticker) VALUES (380, 'MDIA3');
INSERT INTO public.stock (id, ticker) VALUES (381, 'BSLI3');
INSERT INTO public.stock (id, ticker) VALUES (382, 'IGTA3');
INSERT INTO public.stock (id, ticker) VALUES (383, 'GPAR3');
INSERT INTO public.stock (id, ticker) VALUES (384, 'VITT3');
INSERT INTO public.stock (id, ticker) VALUES (385, 'ODPV3');
INSERT INTO public.stock (id, ticker) VALUES (386, 'GMAT3');
INSERT INTO public.stock (id, ticker) VALUES (387, 'VIVT3');
INSERT INTO public.stock (id, ticker) VALUES (388, 'AGXY3');
INSERT INTO public.stock (id, ticker) VALUES (389, 'BALM4');
INSERT INTO public.stock (id, ticker) VALUES (390, 'MRSA5B');
INSERT INTO public.stock (id, ticker) VALUES (392, 'INTB3');
INSERT INTO public.stock (id, ticker) VALUES (393, 'BMOB3');
INSERT INTO public.stock (id, ticker) VALUES (394, 'UGPA3');
INSERT INTO public.stock (id, ticker) VALUES (395, 'BLAU3');
INSERT INTO public.stock (id, ticker) VALUES (396, 'BPAN4');
INSERT INTO public.stock (id, ticker) VALUES (397, 'WSON33');
INSERT INTO public.stock (id, ticker) VALUES (398, 'PTNT3');
INSERT INTO public.stock (id, ticker) VALUES (399, 'JOPA3');
INSERT INTO public.stock (id, ticker) VALUES (400, 'PGMN3');
INSERT INTO public.stock (id, ticker) VALUES (401, 'JPSA3');
INSERT INTO public.stock (id, ticker) VALUES (402, 'BALM3');
INSERT INTO public.stock (id, ticker) VALUES (403, 'RENT3');
INSERT INTO public.stock (id, ticker) VALUES (404, 'BRGE12');
INSERT INTO public.stock (id, ticker) VALUES (405, 'BPAC3');
INSERT INTO public.stock (id, ticker) VALUES (406, 'MTRE3');
INSERT INTO public.stock (id, ticker) VALUES (407, 'BAUH4');
INSERT INTO public.stock (id, ticker) VALUES (408, 'VIVA3');
INSERT INTO public.stock (id, ticker) VALUES (409, 'RAIZ4');
INSERT INTO public.stock (id, ticker) VALUES (410, 'BMIN4');
INSERT INTO public.stock (id, ticker) VALUES (411, 'RPAD6');
INSERT INTO public.stock (id, ticker) VALUES (412, 'POWE3');
INSERT INTO public.stock (id, ticker) VALUES (413, 'RDNI3');
INSERT INTO public.stock (id, ticker) VALUES (414, 'MILS3');
INSERT INTO public.stock (id, ticker) VALUES (415, 'ARZZ3');
INSERT INTO public.stock (id, ticker) VALUES (416, 'PNVL3');
INSERT INTO public.stock (id, ticker) VALUES (417, 'JOPA4');
INSERT INTO public.stock (id, ticker) VALUES (418, 'BOAS3');
INSERT INTO public.stock (id, ticker) VALUES (419, 'BMKS3');
INSERT INTO public.stock (id, ticker) VALUES (420, 'LJQQ3');
INSERT INTO public.stock (id, ticker) VALUES (421, 'BRGE11');
INSERT INTO public.stock (id, ticker) VALUES (422, 'BRGE3');
INSERT INTO public.stock (id, ticker) VALUES (423, 'SULA4');
INSERT INTO public.stock (id, ticker) VALUES (424, 'RPAD3');
INSERT INTO public.stock (id, ticker) VALUES (425, 'SBFG3');
INSERT INTO public.stock (id, ticker) VALUES (426, 'SULA11');
INSERT INTO public.stock (id, ticker) VALUES (427, 'LUXM4');
INSERT INTO public.stock (id, ticker) VALUES (428, 'SULA3');
INSERT INTO public.stock (id, ticker) VALUES (429, 'AFLT3');
INSERT INTO public.stock (id, ticker) VALUES (430, 'TFCO4');
INSERT INTO public.stock (id, ticker) VALUES (431, 'IGTI3');
INSERT INTO public.stock (id, ticker) VALUES (432, 'LIPR3');
INSERT INTO public.stock (id, ticker) VALUES (433, 'STBP3');
INSERT INTO public.stock (id, ticker) VALUES (434, 'CSED3');
INSERT INTO public.stock (id, ticker) VALUES (435, 'IGTI11');
INSERT INTO public.stock (id, ticker) VALUES (436, 'BMIN3');
INSERT INTO public.stock (id, ticker) VALUES (437, 'MULT3');
INSERT INTO public.stock (id, ticker) VALUES (438, 'BRGE8');
INSERT INTO public.stock (id, ticker) VALUES (439, 'NGRD3');
INSERT INTO public.stock (id, ticker) VALUES (440, 'AMBP3');
INSERT INTO public.stock (id, ticker) VALUES (441, 'CCRO3');
INSERT INTO public.stock (id, ticker) VALUES (442, 'ALSO3');
INSERT INTO public.stock (id, ticker) VALUES (443, 'VAMO3');
INSERT INTO public.stock (id, ticker) VALUES (444, 'BRML3');
INSERT INTO public.stock (id, ticker) VALUES (445, 'SOMA3');
INSERT INTO public.stock (id, ticker) VALUES (446, 'MOSI3');
INSERT INTO public.stock (id, ticker) VALUES (447, 'CEGR3');
INSERT INTO public.stock (id, ticker) VALUES (448, 'BRFS3');
INSERT INTO public.stock (id, ticker) VALUES (449, 'RPAD5');
INSERT INTO public.stock (id, ticker) VALUES (450, 'WEGE3');
INSERT INTO public.stock (id, ticker) VALUES (451, 'SCAR3');
INSERT INTO public.stock (id, ticker) VALUES (452, 'ALPA3');
INSERT INTO public.stock (id, ticker) VALUES (453, 'DMVF3');
INSERT INTO public.stock (id, ticker) VALUES (454, 'RADL3');
INSERT INTO public.stock (id, ticker) VALUES (455, 'ALPA4');
INSERT INTO public.stock (id, ticker) VALUES (456, 'LREN3');
INSERT INTO public.stock (id, ticker) VALUES (457, 'CVCB3');
INSERT INTO public.stock (id, ticker) VALUES (458, 'TOTS3');
INSERT INTO public.stock (id, ticker) VALUES (459, 'YDUQ3');
INSERT INTO public.stock (id, ticker) VALUES (460, 'AALR3');
INSERT INTO public.stock (id, ticker) VALUES (461, 'RAIL3');
INSERT INTO public.stock (id, ticker) VALUES (462, 'MGLU3');
INSERT INTO public.stock (id, ticker) VALUES (463, 'NTCO3');
INSERT INTO public.stock (id, ticker) VALUES (464, 'MERC4');
INSERT INTO public.stock (id, ticker) VALUES (465, 'RDOR3');
INSERT INTO public.stock (id, ticker) VALUES (466, 'SYNE3');
INSERT INTO public.stock (id, ticker) VALUES (467, 'AERI3');
INSERT INTO public.stock (id, ticker) VALUES (468, 'ANIM3');
INSERT INTO public.stock (id, ticker) VALUES (469, 'HAPV3');
INSERT INTO public.stock (id, ticker) VALUES (470, 'PETZ3');
INSERT INTO public.stock (id, ticker) VALUES (471, 'SQIA3');
INSERT INTO public.stock (id, ticker) VALUES (472, 'CBEE3');
INSERT INTO public.stock (id, ticker) VALUES (473, 'MERC3');
INSERT INTO public.stock (id, ticker) VALUES (474, 'AMER3');
INSERT INTO public.stock (id, ticker) VALUES (475, 'BIDI3');
INSERT INTO public.stock (id, ticker) VALUES (476, 'BIDI11');
INSERT INTO public.stock (id, ticker) VALUES (477, 'BIDI4');
INSERT INTO public.stock (id, ticker) VALUES (478, 'SEQL3');
INSERT INTO public.stock (id, ticker) VALUES (479, 'VIIA3');
INSERT INTO public.stock (id, ticker) VALUES (480, 'LWSA3');


--
-- Data for Name: valuation; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (2, 'APER3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (3, 'CASH3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (4, 'RCSL3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (5, 'DASA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (6, 'TCNO3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (7, 'MAPT4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (8, 'RCSL4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (9, 'TCNO4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (10, 'NORD3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (11, 'FRTA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (12, 'EMBR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (13, 'ELMD3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (15, 'RRRP3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (16, 'VLID3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (17, 'ORVR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (18, 'TXRX3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (19, 'ECOR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (20, 'TELB3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (21, 'HBSA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (22, 'DTCY3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (23, 'HBRE3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (24, 'SMFT3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (25, 'WEST3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (26, 'FRIO3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (27, 'BIOM3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (28, 'MEAL3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (29, 'AMAR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (30, 'MSPA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (31, 'OPCT3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (32, 'MSPA4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (33, 'TELB4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (34, 'BLUT3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (35, 'TXRX4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (36, 'ENJU3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (37, 'MBLY3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (38, 'IRBR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (39, 'BAHI3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (40, 'PINE4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (41, 'ALPK3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (42, 'CTNM3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (43, 'BKBR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (44, 'ADHM3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (45, 'AHEB3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (46, 'AHEB5', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (47, 'CEED3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (48, 'ESTR4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (49, 'BLUT4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (51, 'SGPS3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (52, 'VIVR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (53, 'SHOW3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (54, 'AZUL4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (55, 'CTNM4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (56, 'OIBR4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (57, 'TCSA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (59, 'GOLL4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (60, 'PLAS3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (61, 'OIBR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (62, 'HOOT4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (63, 'GSHP3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (64, 'COGN3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (65, 'PMAM3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (66, 'ATMP3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (67, 'AVLL3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (68, 'RPMG3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (69, 'MTIG4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (70, 'INEP3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (71, 'INEP4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (72, 'BBRK3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (73, 'JFEN3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (74, 'IGBR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (75, 'BDLL3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (76, 'BDLL4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (77, 'SNSY5', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (78, 'SLED3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (79, 'PDGR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (80, 'TEKA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (81, 'SLED4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (82, 'OSXB3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (83, 'LLIS3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (84, 'TEKA4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (85, 'HETA4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (89, 'CBAV3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (92, 'DOTZ3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (97, 'IFCM3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (98, 'KRSA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (102, 'MODL11', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (103, 'MODL3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (104, 'MODL4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (105, 'NINJ3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (106, 'ONCO3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (108, 'RECV3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (109, 'TRAD3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (112, 'MWET4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (113, 'MWET3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (114, 'MGEL4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (118, 'RSID3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (119, 'GPIV33', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (120, 'TPIS3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (121, 'DMMO3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (122, 'LUPA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (123, 'CTKA4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (124, 'AZEV4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (125, 'BRKM6', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (126, 'HBTS5', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (127, 'AZEV3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (132, 'RNEW4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (133, 'RNEW11', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (134, 'HAGA4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (135, 'RNEW3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (50, 'CRDE3', 68.83, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (86, 'ARML3', 0, 72.35);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (87, 'BRBI11', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (88, 'BRIT3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (90, 'CLSA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (91, 'DESK3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (93, 'FIQE3', 0, 51.99);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (94, 'GETT3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (95, 'GETT4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (96, 'GGPS3', 0, 71.16);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (99, 'LVTC3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (100, 'MATD3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (101, 'MLAS3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (107, 'PORT3', 0, 183.3);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (110, 'TTEN3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (115, 'CEBR5', 74.16, 74.86);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (116, 'CEBR6', 13.05, 74.86);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (117, 'CEBR3', 11.86, 74.86);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (128, 'USIM3', 1.26, 23.38);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (129, 'BAZA3', 41.01, 33.47);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (130, 'CSNA3', 12.57, 20.15);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (131, 'USIM5', 1.39, 23.38);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (136, 'CLSC3', 14.96, 83.85);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (1, 'GNDI3', 2.64, 23.75);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (138, 'CTKA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (139, 'GOAU3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (140, 'MNDL3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (142, 'PETR4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (144, 'PETR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (146, 'MRFG3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (147, 'GGBR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (149, 'TKNO4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (150, 'GOAU4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (151, 'ETER3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (153, 'BRKM3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (155, 'BRKM5', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (157, 'CESP3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (158, 'FHER3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (159, 'BOBR4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (160, 'BRAP3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (161, 'CESP6', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (162, 'TASA4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (163, 'GGBR4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (164, 'TASA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (165, 'BRAP4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (171, 'VALE3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (172, 'JHSF3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (178, 'EPAR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (183, 'CEDO4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (186, 'CTSA4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (188, 'POSI3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (197, 'LAVV3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (208, 'CESP5', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (221, 'MDNE3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (222, 'HBOR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (223, 'PTNT4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (224, 'MNPR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (226, 'CEDO3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (230, 'HAGA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (231, 'CYRE3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (238, 'CTSA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (239, 'SUZB3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (240, 'PFRM3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (242, 'LPSB3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (250, 'CEAB3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (258, 'RANI3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (265, 'MYPK3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (143, 'USIM6', 1.39, 23.38);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (148, 'CPLE6', 4.57, 37.92);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (152, 'PEAB4', 206.92, 69.73);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (154, 'CLSC4', 19.39, 83.85);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (156, 'DOHL4', 4.22, 24.84);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (166, 'PCAR3', 12.17, 29.72);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (167, 'PEAB3', 188.11, 69.73);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (168, 'BGIP4', 38.65, 16.01);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (169, 'EUCA3', 1, 19.69);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (170, 'RAPT4', 3.3, 25.23);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (173, 'DEXP4', 0, 22.07);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (174, 'ALLD3', 0, 16.18);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (176, 'TRPL4', 30.43, 62.83);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (177, 'RAPT3', 3.3, 25.23);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (179, 'DEXP3', 2.83, 22.07);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (181, 'JBSS3', 2.59, 32.14);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (182, 'EALT4', 3.04, 16.97);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (184, 'ENAT3', 27.69, 90.19);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (185, 'CEPE5', 24.42, 78.33);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (187, 'BNBR3', 31.63, 21.28);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (189, 'CGRA4', 30.06, 25.22);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (190, 'CGRA3', 30.06, 25.22);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (191, 'ROMI3', 16.1, 50.47);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (193, 'TAEE11', 40.23, 77.14);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (194, 'TAEE4', 12.7, 77.14);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (195, 'TAEE3', 13.41, 77.14);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (196, 'PATI3', 5.07, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (198, 'ALUP3', 3.3, 36.1);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (199, 'SAPR3', 3.58, 34.63);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (201, 'ALUP11', 9.89, 36.1);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (202, 'POMO3', 1.39, 33.82);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (203, 'BRSR3', 16.18, 40.9);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (204, 'ALUP4', 3.3, 36.1);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (205, 'CEPE6', 26.87, 78.33);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (206, 'BGIP3', 32.25, 16.01);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (207, 'SAPR11', 19.93, 34.63);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (210, 'BBAS3', 29.51, 35.58);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (211, 'UNIP5', 31.71, 63.33);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (212, 'BMEB4', 7.74, 23.15);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (213, 'UNIP6', 30.95, 63.33);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (214, 'VBBR3', 28.07, 58.28);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (215, 'CSRN5', 17.01, 38.97);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (216, 'ENGI4', 2.76, 30.37);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (218, 'UNIP3', 26.49, 63.33);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (219, 'TRPL3', 32.6, 62.83);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (220, 'CMIG4', 6.57, 34.63);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (225, 'CSRN3', 15.46, 38.97);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (227, 'POMO4', 1.38, 33.82);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (228, 'LIGT3', 2.74, 23.75);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (229, 'ENBR3', 10.26, 40.93);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (232, 'PLPL3', 0, 30.26);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (233, 'GEPA3', 60.47, 135.97);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (234, 'GEPA4', 60.47, 135.97);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (235, 'EKTR4', 18.62, 47.4);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (236, 'BEES3', 4.29, 46.01);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (237, 'CRPG6', 19.98, 30.58);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (243, 'EQTL3', 4.97, 20.71);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (246, 'CSRN6', 17.01, 38.97);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (247, 'AGRO3', 11.01, 29.55);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (248, 'SLCE3', 29.3, 49.55);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (249, 'CSMG3', 23.36, 72.16);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (251, 'CRPG5', 19.98, 30.58);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (252, 'PTBL3', 1.94, 54.89);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (253, 'ENGI11', 12.59, 30.37);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (254, 'LEVE3', 19.22, 80.1);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (255, 'WIZS3', 12.5, 87.5);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (256, 'MTSA4', 11.49, 27.33);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (257, 'ITSA4', 11.02, 61.54);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (259, 'ITSA3', 10.99, 61.54);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (260, 'BBDC3', 14.59, 44.02);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (262, 'CMIG3', 5.31, 34.63);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (264, 'ESPA3', 0, 18.61);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (266, 'LOGG3', 2.93, 19.77);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (267, 'SANB3', 16.15, 58.71);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (268, 'ABCB4', 16.03, 44.76);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (269, 'BRSR5', 16.71, 40.9);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (270, 'BEES4', 4.29, 46.01);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (271, 'SHUL4', 2.45, 20.03);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (272, 'CSAN3', 4.73, 30.52);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (141, 'CPLE3', 4.15, 37.92);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (175, 'PATI4', 22.06, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (192, 'CMIN3', 0, 19.88);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (209, 'SAPR4', 3.94, 34.63);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (241, 'CIEL3', 12.14, 59.51);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (244, 'BMGB4', 3.57, 36.21);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (275, 'KLBN4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (282, 'KLBN11', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (289, 'RSUL4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (290, 'ELET6', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (291, 'MOAR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (296, 'ELET3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (298, 'JSLG3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (306, 'BEEF3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (314, 'GUAR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (324, 'KLBN3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (325, 'KEPL3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (327, 'UCAS3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (328, 'LOGN3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (330, 'DIRR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (337, 'GFSA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (338, 'PRNR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (356, 'EVEN3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (357, 'WLMM3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (362, 'TECN3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (364, 'WLMM4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (373, 'ELET5', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (398, 'PTNT3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (400, 'PGMN3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (406, 'MTRE3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (274, 'EMAE4', 16.89, 26.45);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (276, 'CURY3', 0, 48.51);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (277, 'ITUB3', 23.19, 58.83);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (279, 'BPAC5', 1.95, 14.67);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (280, 'SANB11', 34.69, 58.71);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (281, 'EQMA3B', 44.21, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (283, 'SEER3', 13.83, 64.09);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (284, 'EEEL3', 318.72, 67.6);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (285, 'MRVE3', 16.09, 44.91);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (286, 'CAML3', 4.51, 32.03);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (287, 'BBDC4', 18.36, 44.02);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (288, 'VULC3', 0, 36.97);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (292, 'EALT3', 2.27, 16.97);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (293, 'CRIV4', 6.44, 19.45);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (294, 'ITUB4', 23.19, 58.83);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (297, 'DXCO3', 6.57, 84.47);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (299, 'FESA4', 19.04, 48.33);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (300, 'FRAS3', 4.17, 56.92);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (301, 'MOVI3', 4.09, 34.55);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (302, 'TGMA3', 16.2, 50.31);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (303, 'WHRL3', 13.94, 113.47);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (304, 'EZTC3', 16.52, 54.44);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (305, 'REDE3', 2.43, 90.26);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (307, 'CARD3', 5.31, 34.52);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (308, 'EKTR3', 19.03, 47.4);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (309, 'BRIV4', 8.92, 21.47);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (310, 'COCE5', 29.49, 38.98);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (311, 'BRIV3', 2.27, 21.47);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (313, 'CRFB3', 4.9, 39.68);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (316, 'CGAS3', 159.24, 104.05);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (317, 'SBSP3', 19.88, 27.94);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (318, 'FESA3', 17.31, 48.33);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (319, 'COCE3', 29.49, 38.98);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (320, 'CGAS5', 175.15, 104.05);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (321, 'ASAI3', 0, 5.96);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (322, 'CSAB4', 74.06, 29.39);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (323, 'PSSA3', 26.22, 59.66);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (326, 'AURA33', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (331, 'WHRL4', 15.33, 113.47);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (332, 'PDTC3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (333, 'SIMH3', 0, 24.04);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (334, 'GRND3', 4.66, 68.61);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (335, 'BPAC11', 4.86, 14.67);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (339, 'BSLI4', 5.96, 30.85);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (340, 'EQPA3', 2.04, 72.92);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (341, 'BBSE3', 43.6, 95.26);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (342, 'SMTO3', 7.64, 47.87);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (343, 'JALL3', 0, 82.11);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (344, 'QUAL3', 14.89, 77.19);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (345, 'PARD3', 5.8, 39.3);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (347, 'SOJA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (348, 'TUPY3', 19.4, 49.53);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (349, 'ENGI3', 2.5, 30.37);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (350, 'TEND3', 7.48, 22.68);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (351, 'AESB3', 0, 20.68);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (352, 'EGIE3', 43.45, 74.76);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (353, 'OFSA3', 3.83, 23.54);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (355, 'LCAM3', 5.08, 41.94);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (358, 'HYPE3', 19.93, 55.9);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (359, 'SOND5', 47.55, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (360, 'CXSE3', 0, 54.34);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (363, 'CAMB3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (365, 'CPLE5', 7.55, 37.92);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (366, 'BRPR3', 1.51, 38.13);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (367, 'B3SA3', 4.96, 94.09);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (368, 'ENMT3', 27.14, 44.02);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (369, 'ENMT4', 16.96, 44.02);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (370, 'MRSA3B', 12.01, 29.69);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (372, 'PRIO3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (374, 'ABEV3', 8.31, 78.38);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (375, 'MELK3', 0, 92.79);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (377, 'LAME4', 2.18, 56.34);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (378, 'EQPA7', 2.04, 72.92);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (379, 'EQPA5', 2, 72.92);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (380, 'MDIA3', 9.32, 19.29);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (381, 'BSLI3', 5.42, 30.85);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (382, 'IGTA3', 9.54, 33.18);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (383, 'GPAR3', 15.21, 23.75);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (384, 'VITT3', 0, 20.58);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (385, 'ODPV3', 7.25, 65.64);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (386, 'GMAT3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (387, 'VIVT3', 58.34, 85.28);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (388, 'AGXY3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (389, 'BALM4', 4.13, 38.33);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (390, 'MRSA5B', 13.21, 29.69);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (393, 'BMOB3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (394, 'UGPA3', 4.57, 69.63);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (395, 'BLAU3', 0, 15.9);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (396, 'BPAN4', 2.82, 50.64);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (397, 'WSON33', 40.3, 183.3);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (399, 'JOPA3', 13.39, 28.5);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (401, 'JPSA3', 6.08, 10.42);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (402, 'BALM3', 4.13, 38.33);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (403, 'RENT3', 5.15, 27.12);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (404, 'BRGE12', 0.04, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (405, 'BPAC3', 1.91, 14.67);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (407, 'BAUH4', 8.99, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (408, 'VIVA3', 2.29, 20.53);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (278, 'ATOM3', 0, 50.85);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (312, 'CRPG3', 20.35, 30.58);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (329, 'BTTL3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (346, 'BMEB3', 8.02, 23.15);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (361, 'FLRY3', 13.03, 78.04);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (410, 'BMIN4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (413, 'RDNI3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (414, 'MILS3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (425, 'SBFG3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (432, 'LIPR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (433, 'STBP3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (434, 'CSED3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (436, 'BMIN3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (444, 'BRML3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (445, 'SOMA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (448, 'BRFS3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (453, 'DMVF3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (457, 'CVCB3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (460, 'AALR3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (461, 'RAIL3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (463, 'NTCO3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (466, 'SYNE3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (468, 'ANIM3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (471, 'SQIA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (472, 'CBEE3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (475, 'BIDI3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (477, 'BIDI4', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (478, 'SEQL3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (479, 'VIIA3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (14, 'OMGE3', 1.51, 10.64);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (58, 'BAHI11', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (111, 'VVEO3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (137, 'EUCA4', 1.1, 19.69);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (145, 'CPLE11', 0, 37.92);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (180, 'BRSR6', 16.18, 40.9);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (200, 'NEOE3', 7.1, 30.84);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (217, 'CEEB3', 23.75, 49.21);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (245, 'TRIS3', 2.43, 25.08);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (263, 'CRIV3', 0.56, 19.45);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (273, 'EEEL4', 284.42, 67.6);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (315, 'DOHL3', 3.84, 24.84);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (336, 'TIMS3', 0, 33.7);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (354, 'ENEV3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (376, 'LAME3', 2.18, 56.34);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (392, 'INTB3', 0, 20.42);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (422, 'BRGE3', 0.04, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (409, 'RAIZ4', 0, 11.11);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (411, 'RPAD6', 0.01, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (423, 'SULA4', 8.68, 26.27);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (412, 'POWE3', 0, 15.46);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (446, 'MOSI3', 0, 0.16);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (416, 'PNVL3', 1.93, 37.37);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (424, 'RPAD3', 0.01, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (417, 'JOPA4', 11.76, 28.5);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (473, 'MERC3', 3.94, 43.44);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (418, 'BOAS3', 0, 25.67);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (426, 'SULA11', 18.92, 26.27);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (419, 'BMKS3', 278.22, 103.54);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (447, 'CEGR3', 17.8, 97.36);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (420, 'LJQQ3', 1.12, 23.7);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (427, 'LUXM4', 33.69, 137.33);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (421, 'BRGE11', 5.45, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (450, 'WEGE3', 2.85, 49.92);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (428, 'SULA3', 6.78, 26.27);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (474, 'AMER3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (429, 'AFLT3', 5.28, 135.15);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (451, 'SCAR3', 8.69, 27.46);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (430, 'TFCO4', 0, 21.55);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (431, 'IGTI3', 6.08, 10.42);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (452, 'ALPA3', 3.56, 30.97);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (435, 'IGTI11', 0, 10.42);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (476, 'BIDI11', 1.23, 74.52);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (437, 'MULT3', 7.35, 51.85);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (454, 'RADL3', 2.12, 42.88);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (438, 'BRGE8', 4.54, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (439, 'NGRD3', 0, 23.75);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (455, 'ALPA4', 3.92, 30.97);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (440, 'AMBP3', 0, 23.75);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (480, 'LWSA3', 0.53, 81.05);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (441, 'CCRO3', 9.69, 166.15);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (456, 'LREN3', 8.76, 49.84);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (442, 'ALSO3', 7.58, 26.33);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (443, 'VAMO3', 0, 66.97);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (458, 'TOTS3', 2.39, 51.54);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (261, 'CPFE3', 19.06, 49.02);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (459, 'YDUQ3', 12.34, 77.46);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (462, 'MGLU3', 1.69, 32.22);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (295, 'SANB4', 17.73, 58.71);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (464, 'MERC4', 8.43, 43.44);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (465, 'RDOR3', 0, 133.72);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (415, 'ARZZ3', 20.31, 80.87);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (467, 'AERI3', 0, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (469, 'HAPV3', 0.87, 29.89);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (449, 'RPAD5', 7.8, 0);
INSERT INTO public.valuation (id, ticker, price_target, payout) VALUES (470, 'PETZ3', 0.55, 17.96);


--
-- Name: history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.history_id_seq', 480, true);


--
-- Name: price_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.price_id_seq', 480, true);


--
-- Name: stock_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.stock_id_seq', 480, true);


--
-- Name: valuation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.valuation_id_seq', 480, true);


--
-- Name: history history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.history
    ADD CONSTRAINT history_pkey PRIMARY KEY (id);


--
-- Name: history history_ticker_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.history
    ADD CONSTRAINT history_ticker_key UNIQUE (ticker);


--
-- Name: price price_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.price
    ADD CONSTRAINT price_pkey PRIMARY KEY (id);


--
-- Name: price price_ticker_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.price
    ADD CONSTRAINT price_ticker_key UNIQUE (ticker);


--
-- Name: stock stock_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock
    ADD CONSTRAINT stock_pkey PRIMARY KEY (id);


--
-- Name: stock stock_ticker_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock
    ADD CONSTRAINT stock_ticker_key UNIQUE (ticker);


--
-- Name: valuation valuation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.valuation
    ADD CONSTRAINT valuation_pkey PRIMARY KEY (id);


--
-- Name: valuation valuation_ticker_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.valuation
    ADD CONSTRAINT valuation_ticker_key UNIQUE (ticker);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database cluster dump complete
--

